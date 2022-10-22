## 0x08 微积分计算小练习
练习网站存在XSS漏洞，随便乱填一个练习，获得url：`http://202.38.93.111:10056/share?result=MDph`，分析html源码，发现前端会将`result`的值进行`base64`解码(`echo -n MDph | base64 -d`)，获得`user:sorce`格式的字符串，然后用`:`分割用户名和成绩，分别渲染到`"greeting"`和`"score"`中，所以我们可以控制`result`进而控制前端页面，典型的`反射型XSS`。

再分析一下`bot.py`，它是在后端运行的，使用了`selenium`框架提供的`webdriver`模拟了一个浏览器，然后给浏览器设置了`cookie`，`cookie`
的值是flag。

所以我们构造如下`payload`，期望在前端弹出一个`alert`，将`cookie`弹出来。
```
result=$(echo -n "0:<img src=q onerror=alert(document.cookie)>" | base64)
echo "http://202.38.93.111:10056/share?result=$result"
```

将其提交，由于无头浏览器不支持弹窗，触发异常，异常描述里，即可获得flag。
