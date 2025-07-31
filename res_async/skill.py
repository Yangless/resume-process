import re

import pandas as pd
from rapidfuzz import process,fuzz
df=pd.read_csv('res./知识图谱技能带别名.csv')#./res/skill.csv
standard_skills=[i.lower() for i in list(df['0'])]
WORD=re.compile(r'\b(?:[A-Za-z]+\s?)+\b')
def skill_nor(input_skill):
    input_skill=input_skill.lower()
    limit=len(re.findall(r'\s+',input_skill))
    stopwords = {"熟练", "掌握", "了解", "精通", "熟悉"}

    # 使用正则表达式提取完整的英文单词
    words = WORD.findall(input_skill.strip())
    #print(words)

    candidates =words# re.split(r'[\s+|,|\.|/]+', input_skill.strip())#

    cleaned_candidates = []
    for word in candidates:
        cleaned = ''.join([c for c in word if c.isalnum()])
        for stopword in stopwords:
            cleaned = cleaned.replace(stopword, "")
        if cleaned:
            cleaned_candidates.append(cleaned.lower())
    #print(cleaned_candidates)
    # 模糊匹配
    matched_skills = set()
    for word in cleaned_candidates:
        best_match, score, _ = process.extractOne(word, standard_skills, scorer=fuzz.ratio)
        if score>80:
            matched_skills.add(best_match)
        #else:matched_skills.add(word)
    # 输出最多3个结果
    top_skills = list(matched_skills)[:limit+1]
    top_skills=list(set(top_skills))
    return top_skills



    #print("最终匹配结果:", top_skills)
#print(skill_nor('简历与应聘职位匹配度: 81% 李坤  ID:595888931 目前正在找工作 15821966217 likun7854@163.com 男 | 23岁(1996年5月4日)  | 现居住 上海 | 2年工作经验 最近工作 (11个月) 职 位:  Java开发工程师 公 司:  上海博焘网络科技有限公司 行 业:  计算机软件 最高学历/学位 专 业:  计算机科学与技术 学 校:  四川金沙江职业学院 学历/学位:  本科 求职意向 期望薪资:  9000-11000元/月 地点:  上海 职能/职位:  软件工程师 Java开发工程师 行业:  计算机软件 到岗时间:  随时 工作类型:  全职 自我评价:  本人是本科计算机专业,有两年的JAVA开发经验,参与过多个中小型项目的开发工作,如:黑钻星球,优众广告,仟莱信贷等项目. 熟练使用Spring,能熟练与其他框架(SpringBoot,SpringMVC,Mybatis,Hibernate等开源框架)进行组合开发,熟悉J2EE体系结构,对面向对象、MVC有深刻的理解,熟悉运用MySql,Oracle,SQL Server等数据库开发及Tomcat等主流应用服务器,熟练使用常用软件Interllij IDEA,MyEclipse等工具进行系统设计和开发,另外还掌握Maven,swagger,postman,git等常用工具的使用. 有良好的团队交流和合作意识,以及一定的工作压力承受能力,并具有很好的分析问题与解决问题的能力,以及对新知识新技术的学习兴趣. 工作经验 2018/9-2019/8 上海博焘网络科技有限公司 (11个月) 计算机软件|少于50人|民营公司 开发部 Java开发工程师 工作描述:  1.参与设计开发文档或需求说明,完成代码编写、调试、测试和维护,完成软件系统代码注释和开发文档的实现.能独立解决前端反馈的bug以及软件开发过程中的问题,并配合上级领导完成其他相关的工作任务. 2.公司项目分为APP和后台管理系统.个人负责整个黑钻星球后台管理系统的开发,整套系统部署在公司的私有服务器上,主要基于公司的Mysql集群和Redis集群做数据存储,使用MQ集群做消息队列,使用SpringBoot动态数据源进行数据分类,使用Spring,SpringBoot,Maven,数据库MySql进行项目的开发工作,以及swagger,Git,postman等工具的使用.及时与线上APP同步配合,完成对APP所有功能的记录和后台运营人员对项目管理的使用. 2017/7-2018/7 郑州天启信息技术有限公司 (1年) 计算机软件|少于50人|民营公司 开发部 Java开发工程师 工作描述:  主要负责项目的设计需求,部分模块的编写,熟悉软件开发流程,能独完成功能文档的编写和功能模块的测试以及后期维护工作.熟练使用SSM框架,MySql,Maven等进行项目开发,以及SVN,Postman等工具的使用.配合团队完成多个项目的开发,测试以及后续的其他工作. 项目经验 2018/10-2019/7 黑钻星球(博焘)后台管理 所属公司:  上海博焘网络科技有限公司 项目描述:  开发技术和工具:SpringBoot,MySQL,Interllij IDEA,swagger,postman,git 项目描述: 黑钻星球APP汇集在线商城、资讯、游戏、短视频、小说为一体,用户通过使用黑钻星球APP中的各个模块可以获取"黑钻"奖励,"黑钻"可用于商品兑换、消费、交易等.黑钻星球将不定期推出各类奖励活动,积极参与平台活动可获巨额黑钻或 其他奖励. 后台管理系统功能描述: 小说,OTC,联运游戏,在线商城,储蓄罐,竞猜,理财,现金贷,信用卡,命理,用户管理,消息通知,统计报表,第三方登录等 责任描述:  个人负责开发功能: 1.小说:充值记录统计,小说种类排名权重; 2.OTC:内部自动批量挂单(买单,卖单),内部与app用户黑钻交易,内部机器人账号的增删改; 3.联运游戏:充值记录统计,奖励黑钻统计; 4.在线商城:用户购买商品的记录统计,售后转接等; 5.理财功能:储蓄罐的储蓄记录,现金贷和信用卡的申请记录统计;储蓄罐产品,现金贷和信用卡添加,修改和上下架功能; 6.竞猜:单个赛事竞猜,获奖,领奖等记录统计,竞猜赛事关闭和启动功能; 7.用户管理:app用户统计(用户渠道下载来源,黑钻获取渠道来源,充值记录和黑钻总数统计,各功能充值记录和黑钻获取的详细记录统计),权限设置(内部账号,第三方账号); 8.消息通知:app消息中心通知的增改以及推送,otc黑钻交易的交易信息推送; 9.第三方登录:第三方对应产品的充值记录,盈利记录的汇总统计,以及详情记录的展示; 10.其他功能如:命理,征信查询等; 2018/3-2018/7 优众品牌媒体发布管理平台 所属公司:  郑州天启信息技术有限公司 项目描述:  本系统主要功能模块: (1)广告主:广告管理-订单管理-通知/报表管理; (2)网站主:广告位管理-网站管理-订单管理-通知/报表管理; (3)运营商:订单管理-权限管理-用户管理(登陆用户的权限管理)-审核(用户,订单,广告位,广告,机构)-类型管理(广告,广告位)-盈消报表(广告主,网站主,网站); (4)其他:系统首页-注册/登录-广告投放-缓存管理-安全退出... 系统实现目标: 广告管理系统提供广告展示,效果统计,广告管理等功能,实现广告精准投放. 技术描述: 该项目由SSM框架结合传统的MVC所搭建的项目框架.在控制层使用SpringMVC的方法拦截实现登陆的权限功能,使用controller对请求做不同的处理和跳转;运用spring IOC依赖注入实现模型层组建的动态注入.Mybatis作为持久层为提供了更灵活的SQL映射;使用了Ajax(jquery和json)技术实现页面异步无刷新机制,采用Layui插件对后台美化,封装常用组件,增强了用户体验. 责任描述:  个人负责开发功能: 广告主功能模块;网站主功能模块;运营商部分功能模块:审核功能,报表功能 个人中心:账号信息修改,营业执照更换,充值/提现 广告主订单:生成订单,以及订单的信息,订单审核 2017/10-2018/1 扬帆物流管理系统 所属公司:  郑州天启信息技术有限公司 项目描述:  项目描述: 该系统是主要针对物流进行管理的系统.建立一个完善的物流管理系统,能够实现客户订单的生成和拆单,合理安排车辆和司机进行运输调度,有效的仓储管理实现出库订单的拣货、出库;入库订单的收货、入库,能够全程跟踪订单执行状态、车辆运输位置以及货物情况. 模块描述: 订单管理,调度管理,仓储管理,运力管理,跟踪管理,资源管理,用户管理 技术描述: 1.项目前台使用Boorstrap插件,后台使用EasyUI插件,使用AJAX技术实现动态数据刷新. 2. 控制转发层扩展Spring框架的Controller设计理念,同时使用Spring来管理所有的Controller,使用Spring的核心技术IOC可以很好的控制Action的生命周期以及各种服务的注入关系. 3. 持久层使用轻量级框架技术Mybatis来实现ORM处理,同时使用Spring容器来管理持久层. 责任描述:  1、仓储管理:就是负责货物的出库和入库操作.入库就是根据收货单,将收货单中的货物清单收入仓库中,按照收货,预入库,入库确认三个步骤依次执行.预入库就是为收货单指定库位,生成预入库单,具体的库位由仓库+通道+货架组成.每个库位都标明了具体容量和可用容量.出库就是根据拣货单来生成出库单并且修改库存信息.按照预出库,出库确认两个步骤依次执行. 2、用户管理:就是对用户进行管理和维护,并能进行角色授予,仓库授权.基于角色管理进行权限配置.用户角色有接单管理员、拆单管理员、调度管理员、仓库管理员等.可对角色进行权限分配,角色可拥有多个权限. 3.出入库订单管理等 2017/7-2017/10 仟莱信贷管理系统 所属公司:  郑州天启信息技术有限公司 项目描述:  此项目是针对小额贷款公司、信贷机构的专业化业务管理系统. 项目主要基于JavaWeb技术体系,Mysql数据库,Tomcat服务器; 应用Spring/Spring MVC/MyBitis 开源框架搭建系统,采用MVC开发模式: 应用Ajax及jQuery,easyUI 等JS框架 项目简介: 功能模块划分: 用户管理模块:用户注册登录-用户找回密码-用户修改密码-基础资料-用户权限 业务管理模块:业务操作-业务提交-业务进展-业务提醒-业务统计-业务分析 财务管理模块:账单查询-发票打印-账单信息更新与删除 系统管理模块:权限管理 该项目采用J2EE典型的三层结构(视图层、业务层和数据层) 通过Spring+Spring mvc,+Mybatis为主框架来进行实现业务功能, 采用JSP,JQuery,Ajax等前端技术共同完成.每一个业务模块均使用专用接口来实现其功能.使用Spring的依赖注入,控制反转以及面向切面编程的思想. 责任描述:  主要负责用户管理模块和系统管理模块的代码编写与JSP页面的代码编写. 对用户的注册、登录、找回、修改等方面进行校验,校验输入的信息是否符合规定以及用户的信息管理进行分析和代码编写! 教育经历 2013/9-2017/7 四川金沙江职业学院 本科| 计算机科学与技术 附加信息 其他 主题:  专业技能 主题描述:  熟练使用Interllij IDEA,MyEclipse,Eclipse,postman,swagger开发工具;Gitee,GitHub,Xshell 5+Xftp 5进行项目同步开发 ; 熟悉使用MySQL、Oracle、sqlServer、等数据库. 熟悉SpringBoot,SSM(SpringMVC)+Spring+Mybatis,SSH等开源框架. 熟悉tomcat开发服务器,熟练使用Maven,了解Git,SVN版本控制器. 熟悉Redis,rabbitMQ,Spring Boot 动态数据源等. 熟悉servlet、jsp、html、div+css、json、Ajax ,javascript,jQuery. 了解Junit,Log4j等技术和linux系统的基本操作. 熟悉JAVA面向对象编程语言,熟悉J2EE体系结构等;'))
#print(skill_nor('word'))