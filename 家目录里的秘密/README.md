## 0x07 家目录里的秘密
解压全局搜索flag，即可获得`VS Code里的flag`。

再搜索rclone相关文件，发现rclone的配置文件里面有个可疑的密码，根据`https://forum.rclone.org/t/how-to-retrieve-a-crypt-password-from-a-config-file/20051`，解密该密码，即可获得`Rclone里的flag`。
