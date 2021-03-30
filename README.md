[English](README-en.md) | [视频演示](https://www.bilibili.com/video/BV1Zh411f7uu/) | [Live demo!](https://sls-website-ap-beijing-7jlzqqj-1302315972.cos-website.ap-beijing.myqcloud.com/) | [教程](https://juejin.cn/post/6913861424015998989)


# 环境搭建

## 本地测试环境搭建  

实际上，项目中每个拥有 ```serverless.yml``` 文件的目录，都会被传送到云函数的 bucket 中。
而在业务文件夹 scf 中的主入口文件 bootstrap 中有这么一句 
```
RESPONSE=$(LD_LIBRARY_PATH=/opt /opt/ssvm-tensorflow "$_HANDLER" <<< "$EVENT_DATA")
```
就说明，可以在本地安装 ssvm-tensorflow 直接执行测试。

### 准备 ssvm-tensorflow  

#### 下载文件

从 second-stage 的 github 的 ssvm-tensorflow 的 repo 里面，下载 binary package：
docker exec 进入到 docker 容器中的 /app 目录下，然后解压文件  

```
unzip ssvm-tensorflow-0.7.3-manylinux2014_x86_64
cd ssvm-tensorflow-0.7.3-manylinux2014_x86_64/
```

然后运行 ```download_dependencies_all.sh``` 下载 ssvm-tensorflow 的依赖 so 文件。

##### 加速 Binary 的下载速度

如果是国内网，可以使用 fastgit 加速 github 上面 binary 的下载速度。例如可以修改成下面的样子。  

```
wget https://hub.fastgit.org/second-state/ssvm-tensorflow-deps/releases/download/0.7.3/ssvm-tensorflow-deps-TF-0.7.3-manylinux2014_x86_64.tar.gz
tar -zxvf ssvm-tensorflow-deps-TF-0.7.3-manylinux2014_x86_64.tar.gz
rm -f ssvm-tensorflow-deps-TF-0.7.3-manylinux2014_x86_64.tar.gz
ln -sf libtensorflow.so.2.4.0 libtensorflow.so.2
ln -sf libtensorflow.so.2 libtensorflow.so
ln -sf libtensorflow_framework.so.2.4.0 libtensorflow_framework.so.2
ln -sf libtensorflow_framework.so.2 libtensorflow_framework.so
wget https://hub.fastgit.org/second-state/ssvm-tensorflow-deps/releases/download/0.7.3/ssvm-tensorflow-deps-TFLite-0.7.3-manylinux2014_x86_64.tar.gz
tar -zxvf ssvm-tensorflow-deps-TFLite-0.7.3-manylinux2014_x86_64.tar.gz
rm -f ssvm-tensorflow-deps-TFLite-0.7.3-manylinux2014_x86_64.tar.gz
```


#### 增加 so 文件搜索路径  

只是像上面那样下载依赖的 so 文件并且默认的放在 ssvm-tensorlow 相同目录并不能正常使用（这点和 windows 行为不一样），
需要修改文件 ld.so.conf 增加搜索路径

vi /etc/ld.so.conf

```
/app/ssvm-tensorflow-0.7.3-manylinux2014_x86_64
```
然后重新执行装载
```
ldconfig
```

#### 设置 PATH 变量  

修改 bashrc 增加下面的语句使得可以全局使用 ssvm-tensorflow 命令
```
export PATH="/app/ssvm-tensorflow-0.7.3-manylinux2014_x86_64:$PATH"
```
别忘记 source ~/.bashrc

## 准备输入数据  

从 main.rs 可以看到 input 为 STDIN 而且 output STDOUT，因此可以使用 bash 的管道操作直接进行测试。
其中 input 的数据结合 website/content/index.html 可以看到是 post 的 json 数据。这个数据可以方便的通过
直接打开 index.html 然后在 chrome 里面的开发者工具中直接在 console 中打出结果，例如下面的语句增加到网页里面

```
console.log("111111");
console.log(reader.result.split("base64,")[1]);
console.log("111111");
```
我已经将 images 文件夹下的一张猩猩图片，通过网页 submit 然后在 console 中获得了数据写在了 ```image1.postData``` 里面。

## 执行本地测试  

首先在容器外面执行  
```
 ssvmup build --enable-ext --enable-aot

```

对文件进行编译，由于使用的不是 ubuntu 环境， enable-aot 参数会被忽略，但是不影响本地测试。


在容器中执行

```
 cat src/image1.postData| ssvm-tensorflow pkg/scf.wasm
```


# 发布上线  

在容器中或 ubuntu 20.04 版本中执行编译：

```
cd /app && ssvmup build --enable-aot --enable-ext && cp pkg/scf.so scf/  && sls deploy
```

然后在腾讯云 console 中，进入“函数服务” -- “函数管理”，右键一个文件，选择 “在集成终端中打开”， 确保自己在文件目录下，可能是在

```
/usr/local/var/functions/ap-shanghai/lam-pxmnxfm2/tf-scf-prod-AIaaS-template
```

然后执行下面命令让 bootstrap 文件有执行权限。  

```
chmod -R 777 .
```

最后选择上面的 ```部署``` 按钮。


# 模型调试  

这里我们更换了一个 tensorflow 提供的 mobiletnet 中的量化模型 ```mobilenet_v1_1.0_224_quant```， 
该模型可以识别 1000 多种物体种类。我们首先在 python 中获取其 input 和 output 的 tensor 维度信息以及 layer name。

```
python fine-tuning.py
```
得到下面的信息：   

|  Item   | Value  |
|  ----  | ----  |
| input demension | [1, 224, 224, 3] |    
| input layer name | input |  
| output layer name |  MobilenetV1/Predictions/Reshape_1 |   



按照上面的信息修改 main.rs 文件，否则 output 的 res_vec 一直都是 0
