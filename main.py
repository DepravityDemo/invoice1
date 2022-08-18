from invoice.invoice import *















if __name__ == "__main__":
    error_list = [] #初始化错误文件列表
    all_pdf = get_all_pdf()#获取当前目录所有pdf文件
    fp_data = get_exist_data()#获取现有数据 返回字典
    pdf_list = get_undeal_pdf()#获取新数据
    print(pdf_list)# 打印未处理pdf
    for i in pdf_list:
        fp_content = get_invoce_data(i)
        fp = get_invoce_class(fp_content,i)
        ret = fp.print_check_sheet(i)
        name = rename_pdf(i,fp)
        fp_data.append(fp_content)
        if (ret==1):
            error_list.append(fp.fp_name)
        else:
            print(fp.fp_name, '处理成功')

    print('error_list:')
    for i in error_list:
        print(i)


    with open("fp_data.json",'wb') as f:
        f.write(json.dumps(fp_data).encode('utf-8'))



    # # fp = get_invoce_data('25.50_电笔_钢盾_电笔.pdf')
    # # ret = fp.print_check_sheet('25.50_电笔_钢盾_电笔.pdf')
    #     if (ret==1):
    #         error_list.append(fp.fp_name)
    #     else:
    #         print(fp.fp_name, '处理成功')
    # print('error_list:')
    # for i in error_list:
    #     print(i)





