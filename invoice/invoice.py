
import urllib
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
import math
import requests
import os
import xlrd
from xlutils.copy import copy


with open('baidu_auth','r') as f:
    baidu_secrets = json.loads(f.read())




class Invoice(object):
    def __init__(self,fp_content,pdf_name):
        self.InvoiceCode = fp_content['InvoiceCode'] #发票代码
        self.InvoiceNum = fp_content['InvoiceNum'] #发票号码
        self.SellerName = fp_content['SellerName']  #销售商
        self.AmountInFiguers = fp_content['AmountInFiguers'] # 总价
        self.CommodityName = fp_content['CommodityName']  # 商品名 需要搭配[row]['word']
        self.CommodityType = fp_content['CommodityType'] # 商品类型 需要搭配[row]['word']
        self.CommodityNum=fp_content['CommodityNum'] # 商品数量 需要搭配[row]['word']
        self.CommodityUnit=fp_content['CommodityUnit'] # 商品数量 需要搭配[row]['word']
        #self.CommodityTaxRate= fp_content['CommodityTaxRate'] if fp_content['CommodityTaxRate'] not in ["免税","***"] # 商品税率 需要搭配[row]['word']
        self.CommodityTax= fp_content['CommodityTax'] # 商品税额 需要搭配[row]['word']
        self.CommodityAmount= fp_content['CommodityAmount'] # 商品金额 需要搭配[row]['word']
        self.fp_name = pdf_name
    def get_invoice_num(self):
        return self.InvoiceNum
    def get_invoice_seller(self):
        return self.SellerName
    def print_check_sheet(self,pdf_name):
        error_flag = 0
        wb = xlrd.open_workbook('1.xls') #打开模板文件
        cur_row = wb.sheets()[0].nrows #获取当前行号
        wbook = copy(wb) #复制为可写
        ws = wbook.get_sheet(0) # 激活当前工作表
        flag = 0
        total = 0
        error_file = []
        for i in range(len(self.CommodityName)):#遍历所有行
            if (flag == 1):
                flag = 0
                continue
            #(float(self.CommodityTax[i]['word'] if self.CommodityTax[i]['word'].isdigit() else 0)
            try:
                self.CommodityTax[i]['word'] = float(self.CommodityTax[i]['word'])
            except:
                self.CommodityTax[i]['word']=0.0

            # if((i+1<len(self.CommodityName)) and (i+1>=len(self.CommodityNum))):
            #     a = float(self.CommodityAmount[i]['word']) +  float(self.CommodityTax[i]['word'])
            #     b = float(self.CommodityAmount[i+1]['word']) +  float(self.CommodityTax[i+1]['word'])
            #     sum = round(a-b,2)
            #     flag = 1
            # else:
            sum = round(float(self.CommodityAmount[i]['word'])+self.CommodityTax[i]['word'],2)
            total+=sum
            ws.write(cur_row, 0, self.CommodityName[i]['word'][-10:])
            try:
                ws.write(cur_row, 3, self.CommodityUnit[i]['word'] if i<len(self.CommodityUnit) else self.CommodityUnit[0]['word'])
            except:
                ws.write(cur_row, 3,'个')
            try:
                ws.write(cur_row, 4, self.CommodityNum[i]['word'])
            except:
                ws.write(cur_row, 4,'未知')
            try:
                ws.write(cur_row, 5, round(sum/float(self.CommodityNum[i]['word']),2))
            except:
                ws.write(cur_row, 5, '未知')
            ws.write(cur_row, 6, sum)
            cur_row +=1
        wbook.save('1.xls')
        if (math.isclose(total, float(self.AmountInFiguers), rel_tol=1e-5)):
            error_flag = 0
        else:
            error_flag = 1
        return error_flag




def get_auth_key():
    """
    获取认证权限，返回access_token
    :return:
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": baidu_secrets['api_key'],
        "client_secret": baidu_secrets['secret_key']
    }
    s = requests.post(baidu_secrets['auth_url'], data=data)
    return json.loads(s.text)['access_token']


def get_invoce_data(pdf_name):
    """
    解析发票数据，返回发票类
    :param pdf_name:
    :return: class Invoice
    """
    m_request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice"
    f = open(pdf_name, 'rb')
    # print(f.read());
    pdf = base64.b64encode(f.read())
    params = {"pdf_file": pdf}
    access_token = get_auth_key()
    m_request_url = m_request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(m_request_url, data=params, headers=headers)
    fp_content = response.json()['words_result']
    fp = Invoice(fp_content,pdf_name)
    return fp




def get_all_pdf():
    """
    获取当前目录所有pdf
    :return:
    """
    pdf_list = []
    for i in os.listdir():
        if ".pdf" in i:
            pdf_list.append(i)
    return pdf_list


def get_num_and_coperate():
    pdf_list = get_all_pdf()
    num = ""
    name = ""
    for i in pdf_list:
        fp = get_invoce_data(i)
        num+=fp.get_invoice_num() + ";"
        name+=fp.get_invoice_seller() + ";"
    print(num)
    print(name)




def rename_pdf(pdf_name,fp):
    name = json.loads(get_abstract(fp.CommodityName[0]['word']))['data']['ke'][0]['word'] +'_'+\
           json.loads(get_abstract(fp.CommodityName[0]['word']))['data']['ke'][1]['word'] +'_'+\
           json.loads(get_abstract(fp.CommodityName[0]['word']))['data']['ke'][0]['word']
    new_name = fp.AmountInFiguers + '_' + name + ".pdf"
    os.rename(pdf_name, new_name)
    print("rename:",pdf_name,"to",new_name)


def get_abstract(TEXT):
    with open('xf_auth') as f:
        xf_secret = json.loads(f.read())
    url = xf_secret['url']
    api_key =  xf_secret['api_key']
    x_appid =  xf_secret['x_appid']
    body = urllib.parse.urlencode({'text': TEXT}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    #json.loads(result.decode('utf-8'))['data']['ke'][0]['word']
    return result.decode('utf-8')




if __name__ == "__main__":
    get_num_and_coperate()
