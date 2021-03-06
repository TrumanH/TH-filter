A filter which has expire feature and efficiency are compareable with bloomfilter.

keyword: bitmap matrix expire automatic configuration.

一个配置可选自动过期功能的去重过滤器。性能与bloomfilter相当,
但长久使用内存更友好，误判率稳定。因为bitmap使用次数与误判率正相关    
导致需持续增加bitmap大小(内存)以防止误判率升高，且有哈希分布不均，   
往期特征无法过期作废等潜在问题。
#### Configurations:


#### 背景：
黑名单爬虫采集推荐系统等各种场景中经常需要用到去重过滤，类似场景很多人第一反应就是到开源一搜有就拿来用...
恰好也确实有这么一个还不错的去重过滤器：bloomfilter
它有优秀的设计思想：一个条目通过HashMap映射出多个bitmap内一组(一般6~8个)偏置位(offset),   
setbit置入特征，exist通过检查此条目映射出的特征（一组偏置位offset）是否已经被置位来判断    
是否已存在。良好的时间复杂度（置入和判重都是O(1)），极高的空间利用效率...... 

但bloomfilter真的好到能无缺陷的解决去重场景下的所有问题吗？详细了解后发现并非如此。
有句话这么说的：好的程序员是过单行线马路都要两边张望的。
网上关于它反面的声音同样也有很多有些说的很详细
高性能的Bloomfilter并非完美，从解决方案来说甚至算不上完整或完善，长久使用有诸多缺陷，    
简单概括有以下几点：   

1.单向递增位图误判率与使用次数天然正相关。  
2.长久使用为保障准确率须持续扩容，内存会越撑越大。  
3.哈希分布不均的潜在问题（影响准确率）--没人统计验证不代表不存在， 
按照量变引起质变原则，有些问题是在数据量累积到一定程度后必然会出现的。     

于是想上面这些问题是如何导致的呢？根本原理是什么？否可以通过设计从根本上规避掉上面的问题？
思考上面问题后有如下结论：   
根本是位图offset有重复覆盖无法根据日期记录从而导致特征置入不可撤销。如果强行记录
(比如考虑过的使用计数矩阵方案)又会破环效率且增加很多不必要的复杂度。
但如果通过周期轮换构建的方式，底层还是使用高效的bitmap，所以时间复杂度不变（置入和判重都是O(1)），
长久使用空间使用稳定误判率稳定，且考虑到有不想使用过期的可能通过配置可选的方式将选择权交还给用户。
这样的话，可以达到效率不损失的前提下，解决前面提到的缺陷问题。  
综合起来，自己构建一个过滤器理想情况能达成如下要求(已基本达成)：  
1.与Bloomfilter性能相当(时间复杂度为同一等级)。     
2.带有可配置的自动过期功能。所以初始空间会比Bloomfilter稍高，但长久使用的话
内存空间占用反而比bloomfilter低很多，且误判率天然更加稳定。     
3.哈希采用尽可能均匀分布的算法。   
4.沉默待使用特征持久化处理以节省内存空间，仅用时(轮动更新)加载入Redis计算使用，以及过程中的压缩和解压缩。

实现之前网上也找了找，似乎没有开源好用的符合要求的同类东西。应该不算重复造轮子吧~
*尝试在哈希均匀分布及压缩效率上做出一点改进*

#### 概要
内存里同时存在两个 bitmap:   
一个为今天的today(bitmap1)，一个为前期的history(bitmap0)；    

bitmap1(today)则作为实时使用的bitmap根据使用常常更新，同时每到周期时间点
初始化更新一次。

bitmap0(history)每到周期点计算更新一次.


#### 典型的一次周期更新策略为：
1.bitmap1(today) rename 为 history_1 且set in(合并)入 刚初始化新的history(原来的history改名为old_histroy并在更新期间依然生效使用)，
同时初始化一个新的bitmap1(today)。

2.从持久化的files中依次取出 history_2, history_3 ...   
且依次 bitop or (特征合并入) history。(完成后新history即计算得出)
3.删除旧的old_history，此时，周期更新其实已经完成正常使用。      
4.最后除了today history, 其它所有bitmap 命名+1 存为本地文件后 从redis中删除del。
实际仅需将本地文件history_2,history_3...全部命名+1处理(其实可放在2当中同时处理)，
然后将Reids中的history_1 持久化为本地文件 histroy_2,完成后在redis中删除history_1。

That's all,就这么简单。

*不使用持久化版本就逻辑简单些(但占用内存更多且不必要)（history_1, history_2 rename 命名+1处理...）*

#### 使用原理
本质上和bitmap一样，都是通过HashMap置入特征，但通过周期轮动更新来带来自动(定时)过期的功能.   
由此带来的使用上的变化：    
1.典型的情况下新来一个feature，exist现在需要在bitmap0(history)和bitmap1(today)中同时判断，
有一个True即为True,为重复项。(today需要set in置位。)     
2.两个都False才为False。(也需要将today set in置位)    
3.bitmap1(today)是代表今天的特征位图，可见任何情况来一个feature都需要在它其中
set in置位。虽然其中bitmap1 exist判断已经True的时候set in无意义。   

#### 附注：
Redis里面bitmap的存储方式是(压缩后的)每2位16进制字符串为元素单位进行的， 
每个(2位)16进制数负责代表8位bit; 16**2 = 256 = 2**8
比如： \xa0 python 里16进制表示为 0xa0  int('0xa0', 16)=160  
转换为 十进制及二进制分别为：
int('0xa0',16)=160  
bin(160) = '0b10100000' 
6,8 bit 位为1

#### 命名策略暂定为：
today   
history           
history_1       
history_2   
histroy_3
...

文件始终仅存
history_1,
history_2,   
histroy_3,
...
