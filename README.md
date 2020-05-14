A filter which has expire feature and efficiency are compareable with bloomfilter.

keyword: bitmap matrix expire automatic configuration.

#### Configurations:
生产中需要用到过滤器，但高性能的Bloomfilter单向递增位图有着误判率与使用次数正相关的天然缺陷。  
遂自己构建一个过滤器，要求：  
1.与Bloomfilter性能相当(时间复杂度为同一等级)。
2.带有可配置的自动过期功能。(所以空间复杂度会比Bloomfilter稍高)

市面上找了找，好像没有特别好用的符合要求的同类东西。应该不算重复造轮子吧~(即便有也就当练手了...) 
原理不是太复杂，没有涉及什么高深的算法，就是有一点矩阵运算，另外还有些压缩优化之类的，可能看到这有人已经能猜出来我要干嘛了...



