# -*- coding: utf-8 -*-
# flake8: noqa

import tkinter
import tkinter.filedialog as filedialog
import os
from tkinter import ttk
import time
from pprint import pprint
import json
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import pyperclip

class MainWindow():
    def  __init__(self):
        self.root = tkinter.Tk()
        self.root.title("图片自动上传工具  V1.0  By orzangleli")
        #标题
        self.title = tkinter.Label(self.root,text ="七牛 图片自动上传工具",height = 2,width = 80)
        self.title.grid(row = 0,column = 1)

        #Access Key
        self.access_key = tkinter.Label(self.root,text ="Access Key:",height =1,width =20)
        self.access_key.grid(row = 1,column = 0)
        self.access_key_value = tkinter.Entry(self.root,width = 80)
        self.access_key_value.grid(row = 1,column = 1)

        #Secret Key 
        self.secret_key = tkinter.Label(self.root,text ="Secret Key:",height =1,width =20)
        self.secret_key.grid(row = 2,column = 0)
        self.secret_key_value = tkinter.Entry(self.root,width = 80)
        self.secret_key_value.grid(row = 2,column = 1)

        #Bucket Name
        self.bucket_name = tkinter.Label(self.root,text ="Bucket Name(空间名):",height =2,width =20)
        self.bucket_name.grid(row = 3,column = 0)
        self.bucket_name_value = tkinter.Entry(self.root,width = 80)
        self.bucket_name_value.grid(row = 3,column = 1)

        #Select FileFolder
        self.select_filefolder = tkinter.Button(self.root,text= "选择文件夹",height = 1,width =10)
        self.select_filefolder.grid(row = 4,column = 0)
        self.select = tkinter.Entry(self.root,width =80)
        self.select.grid(row = 4,column = 1)
        
        
        
        #Upload
        self.upload = tkinter.Button(self.root,text= "批量上传",height = 1,width =10)
        self.upload.grid(row = 5,column = 0)
        self.info = tkinter.Label(self.root,text ="提示：上传成功后，右键即可复制外链",height =1,width =80)
        self.info.grid(row = 5,column = 1)
        #文件列表
        #self.listbox_files = tkinter.Listbox(self.root, width=80)
        #self.listbox_files.grid(row = 6,column =1)

        # 定义中心列表区域
        self.tree = ttk.Treeview(self.root, show="headings", height=10, columns=("a", "b", "c","d"))
        self.vbar = ttk.Scrollbar(self.root, orient="vertical")
        # 定义树形结构与滚动条
        self.tree.configure(yscrollcommand=self.vbar.set)
        # 表格的标题
        self.tree.column("a", width=50, anchor="center")
        self.tree.column("b", width=200, anchor="center")
        self.tree.column("c", width=200, anchor="center")
        self.tree.column("d", width=200, anchor="center")
        self.tree.heading("a", text="编号")
        self.tree.heading("b", text="文件名")
        self.tree.heading("c", text="成功")
        self.tree.heading("d", text="外链")
        self.tree.grid(row=6, column=1, sticky="NSWE")
        self.vbar.grid(row=6, column=2, sticky="NS")


        #绑定响应
        self.select_filefolder.bind("<ButtonRelease-1>",self.select_directory_listener)
        self.upload.bind("<ButtonRelease-1>",self.upload_listener)

        self.context_menu = tkinter.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="上传", command=self.single_img_upload)
        self.context_menu.add_command(label="复制", command=self.copy_handler)
        self.tree.bind('<3>', self.show_context_menu)

        self.directory = None

        try:
            self.config_file = open("config_data.txt",encoding="UTF-8")
            content = self.config_file.read()
            if len(content) > 10:
                m_config_data = json.loads(content)
                self.access_key_value.insert("end",m_config_data["AccessKey"])
                self.secret_key_value.insert("end",m_config_data["SecretKey"])
                self.bucket_name_value.insert("end",m_config_data["BucketName"])
                self.select.insert("end",m_config_data["Directory"])
                if self.select.get() is None:
                    pass
                else:
                    self.directory = self.select.get()
                    self.files = os.listdir(self.directory)
                    #重新导入文件夹，只保留图片格式
                    temp_files = []
                    for file in self.files:
                        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".gif"):
                            temp_files.append(file)
                            pass

                    self.files = temp_files   
                
                    index = 0
                    ##数据
                    self.list_data = []
                    for file in self.files:
                        item_data = {"a":(index+1),"b":file.split("/")[-1],"c":"未上传","d":"无"}
                        self.list_data.append(item_data)
                        self.tree.insert("","end",values = (self.list_data[index]["a"],self.list_data[index]["b"],self.list_data[index]["c"],self.list_data[index]["d"]))
                        index = index + 1

            self.config_file.close()
        except:
            print("未找到配置文件，准备创建")
        
        self.root.mainloop()
    
    def select_directory_listener(self,event):
        for _ in map(self.tree.delete, self.tree.get_children("")):
            pass
        self.directory = filedialog.askdirectory()
        self.select.delete(0,"end")
        self.select.insert("end",self.directory)
        self.files = os.listdir(self.directory)
        
        #只保留图片格式
        temp_files = []
        for file in self.files:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".gif"):
                temp_files.append(file)
                pass

        self.files = temp_files   
    
        index = 0
        ##数据
        self.list_data = []
        for file in self.files:
            item_data = {"a":(index+1),"b":file.split("/")[-1],"c":"未上传","d":"无"}
            self.list_data.append(item_data)
            self.tree.insert("","end",values = (self.list_data[index]["a"],self.list_data[index]["b"],self.list_data[index]["c"],self.list_data[index]["d"]))
            index = index + 1

    def upload_listener(self,event):
        if self.access_key_value.get() is None:
            tkinter.messagebox.showerror("错误", "请先填写Access Key")
            return 'break'
        if self.secret_key_value.get() is None:
            tkinter.messagebox.showerror("错误", "请先填写Secret Key")
            return 'break'
        if self.bucket_name_value.get() is None:
            tkinter.messagebox.showerror("错误", "请先填写Bucket Name")
            return 'break'
        if self.select.get() is None:
            tkinter.messagebox.showerror("错误", "请先选择待上传的目录")
            return 'break'
        #将数据保存至配置文件
        config_data = """{"AccessKey":"%s","SecretKey":"%s",
                       "BucketName":"%s","Directory":"%s"}"""%(self.access_key_value.get(),self.secret_key_value.get(),self.bucket_name_value.get(),self.select.get())
        self.config_file = open("config_data.txt","w+",encoding="UTF-8")
        self.config_file.write(config_data)
        self.config_file.close()
        
        index = 0
        for file in self.files:
            try:
                localfile = "/".join((self.select.get(),file))
                key = self.uploadImage(localfile)
            except Exception as e:
                self.list_data[index]["c"] = "失败"
                print(e)
            else:
                self.list_data[index]["c"] = "成功"
                self.list_data[index]["d"] = "![](http://%s.qiniudn.com/%s?imageView2/0/w/600)"%(self.bucket_name_value.get(),key)
            index = index + 1
        self.refresh_table()
        

        
    def refresh_table(self):
        # 删除原节点
        for _ in map(self.tree.delete, self.tree.get_children("")):
            pass
        #插入新的
        index = 0
        for file in self.files:
            #数据
            self.tree.insert("","end",values = (self.list_data[index]["a"],self.list_data[index]["b"],self.list_data[index]["c"],self.list_data[index]["d"]))
            index = index + 1

    def uploadImage(self,localfile):
        q = Auth(self.access_key_value.get(), self.secret_key_value.get())
        bucket_name = self.bucket_name_value.get()
        #服务器上的文件名
        key = "%s_%s"%(self.GetNowTime(),localfile.split("/")[-1])
        token = q.upload_token(bucket_name, key, 3600)
        #要上传文件的本地路径
        put_file(token, key, localfile)
        #ret, info = put_file(token, key, localfile)
        #print(info)
        return key

    def GetNowTime(self):
        return time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))

    def show_context_menu(self,event):
        self.context_menu.post(event.x_root,event.y_root)
        self.click_position = {"x":event.x,"y":event.y}
 
    def copy_handler(self):
        row = self.tree.identify_row(self.click_position["y"])
        vals = self.tree.item(row, 'values')
        pyperclip.copy(vals[3])

    def single_img_upload(self):
        row = self.tree.identify_row(self.click_position["y"])
        vals = self.tree.item(row, 'values')
        if vals[3] == "无":
            try:
                localfile =  "%s/%s"%(self.select.get(),vals[1])            #"/".join((self.select.get(),vals[1]))
                key = self.uploadImage(localfile)
            except Exception as e:
                self.list_data[self.tree.index(row)]["c"] = "失败"
                print(e)
            else:
                self.list_data[self.tree.index(row)]["c"] = "成功"
                self.list_data[self.tree.index(row)]["d"] = "![](http://%s.qiniudn.com/%s?imageView2/0/w/600)"%(self.bucket_name_value.get(),key)


        self.refresh_table()
            
        


mainWindow = MainWindow()




















