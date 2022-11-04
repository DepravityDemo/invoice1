import requests
s = requests.get('https://nnfp.jss.com.cn/HHF2tB4a-ey3RVc')
print(s.text)
with open('1.pdf','wb+') as f:
    f.write(s.content)


