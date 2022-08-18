from invoice.invoice import *

if __name__ == "__main__":
    #get_num_and_coperate() #获取发票号和开票公司
    error_list = []
    path ="C:/Users/Depravity/OneDrive/发票/发票打印/已打印/"
    pdf_list = get_all_pdf()
    for i in pdf_list:
        fp = get_invoce_data(i)
        ret = fp.print_check_sheet(i)
        rename_pdf(i,fp)
    # fp = get_invoce_data('25.50_电笔_钢盾_电笔.pdf')
    # ret = fp.print_check_sheet('25.50_电笔_钢盾_电笔.pdf')
        if (ret==1):
            error_list.append(fp.fp_name)
        else:
            print(fp.fp_name, '处理成功')
    print('error_list:')
    for i in error_list:
        print(i)






