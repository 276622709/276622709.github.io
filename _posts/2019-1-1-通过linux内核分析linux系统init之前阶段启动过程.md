很早之前就对Linux内核很感兴趣，最近突然又遇到linux启动过程的问题，参考《linux内核0.11完全注释》记录下学习中的过程和想法，方便之后进行复习和回忆  
1.首先计算机开机后，从一个内存地址开始执行程序，这个地址是计算机出厂的时候就规定好的，这个地址指向bios  
2.bios开始执行自检，初始化中断向量程序，以便之后的程序可以调用，然后加载可启动设备的第一个扇区加载到内存地址0x7C00处  
3.这里第一个扇区即为bootsect.s编译后的内容，bootsect.s的作用是，现将自己的代码从0x7C00移动到0x90000处，再将setup.s编译后的内容读入到内存地址  
0x90200处，最后将system模块内容加载到0x10000处，然后将cs，ip指向setup.s代码处，执行setup代码  
bootsect.s代码200多行主要内容如下  
1）定义一些变量 变量的值是一些地址初始位置  
2）移动代码，将bootsect自身代码从0x7c00处移动到0x90000处，并重置一些段寄存器的值  
3）使用bios中断int0x13将包含setup.s程序的磁盘扇区第2-5位置的扇区加载到0x90200位置处  
4）在屏幕上显示一些字符串"loading system...."  
5）加载system模块到内存地址0x10000处(这里用到了read_it子程序)  
6）关闭驱动器马达（这里用到了kill_motor子程序）  
7）改变cs,ip值，指向setup.s所在内存地址处，然后将指挥权交给setup.s代码  
4.setup.s代码260行主要内容如下  
1)将system代码从0x10000处移动到0x00000处  
2)通过bios调用获取光标信息，内存信息，显存信息，磁盘参数信息并保存到0x90000-0x901FC地址处，即原来的bootsect.s代码所在的地址处  
3)接着进入32位保护模式的操作，定义各种参数，加载全局描述符表寄存器，继而通过寄存器中保存的全局描述符表地址，加载全局描述符表中第一个段描述符项  
4)通过加载的第一个段描述符项中的基地址0和跳转命令中的偏移地址0，跳转到system所在模块0x00000处，接下来执行system模块  
5.system模块的最前面是head.s文件代码，先执行head.s代码  
1）初始化中断描述符表中的256项门描述符  
2）检查A20门地址是否打开  
3）初始化内存页目录表  
4）跳转到init.c中  

之后执行init程序初始化  
