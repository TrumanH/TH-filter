A filter which has expire feature and efficiency are compareable with bloomfilter.

keyword: bitmap matrix expire automatic configuration.

#### Configurations:
生产中需要用到过滤器，但高性能的Bloomfilter长久使用有诸多缺陷
1.单向递增位图误判率与使用次数天然正相关。  
2.长久使用为保障准确率须持续扩容，内存会越撑越大。
3.哈希分布不均的潜在问题（影响准确率），没人统计验证不代表不存在，恰恰相反，
按照量变引起质变原则，有些问题是在数据量累积到一定程度后必然会出现的。

遂自己构建一个过滤器，要求：  
1.与Bloomfilter性能相当(时间复杂度为同一等级)。 
2.带有可配置的自动过期功能。所以初始空间会比Bloomfilter稍高，但长久使用的话
内存空间占用反而比bloomfilter低很多。    
3.哈希采用尽可能均匀分布的算法。   

市面上找了找，好像没有特别好用的符合要求的同类东西。应该不算重复造轮子吧~(即便有也就当练手了...) 
原理不是太复杂，没有涉及什么高深的算法，就是有一点矩阵运算，另外还有些压缩优化之类的，可能看到这有人已经能猜出来我要干嘛了...

内存里同时存在两个 bitmap:   
一个为今天的today(bitmap)，一个为前期的history(bitmap)；    

bitmap1则作为实时使用的bitmap根据使用常常更新，同时每到过期点(00:0000)
初始化(全零)大更新一次。

history(bitmap)每天(00:0000后)更新一次，更新策略为：
由today(bitmap)(全零初始化)更新触发，
每当bitmap1全零初始化后，产生了bitmap1_old(旧bitmap1).
由bitmap1_old合并(所有元素对应或运算)入bitmap0_new, 
bitmap0_new由硬盘里持久化存储的历史所有天(不含刚成为的最老的一天)的bitmap和(所有元素或)而成。

bitmap0_new替换成为新的bitmap0.

由此带来的使用上的变化：
1.新来一个feature，exist现在需要在bitmap0和bitmap1中同时判断，
有一个True即为True,为重复项。(bitmap1需要set in置位。)
2.两个都False才为False。(也需要将bitmap1 set in置位)
3.因为bitmap1是代表今天，所以任何情况来一个feature都需要在它其中
set in置位。其中bitmap1 exist判断已经True的时候set in无意义。


Redis里面bitmap的存储方式是(压缩后的)每2位16进制字符串为元素单位进行的， 
每个(2位)16进制数负责代表8位bit; 16**2 = 256 = 2**8
比如： \xa0 python 里16进制表示为 0xa0  int('0xa0', 16)=160  
转换为 十进制及二进制分别为：
int('0xa0',16)=160  
bin(160) = '0b10100000' 
6,8 bit 位为1

#### 命名策略为：
today
history_1
history_2
history_3  (过期时间为3天时)
...
