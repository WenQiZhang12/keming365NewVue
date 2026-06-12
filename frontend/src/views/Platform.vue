<template>
  <div class="platform-page">
    <!-- Hero Section -->
    <div class="section test1">
      <div class="jianjie2">
        <span class="title">科 明 3 6 5 V R 教 学 云 平 台</span>
        <span class="subtitle">本平台资源涵盖数十个专业，分为VR课堂教学资源及虚拟仿真实验教学资源。</span>
      </div>
    </div>

    <!-- VR Classroom Section -->
    <div class="section test2">
      <div class="jianjie2">
        <span class="title">一、VR课堂教学资源</span>
        <div class="content">
          <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;教学资源按照高等学校机械类专业教学指导委员会机械类专业的培养计划及各课程教学大纲的要求，充分利用VR/AR等技术开发而成，体现"三维可视化及互动学习"的特点，各课程开发了90~140余个碎片化知识点VR教学资源。教师及学生在各课程的栏目中下载VR教学资源的教学PPT，只要用户终端（电脑、手机等）处于上网状态，即可在教学过程中使用这些VR资源，任意缩放、交互操作，让抽象的理论知识立体化、形象化、直观化，充分调动学生的主观能动性和思维能力。</span>
        </div>
      </div>
    </div>

    <!-- Virtual Lab Section -->
    <div class="section test3">
      <div class="jianjie2">
        <span class="title">二、虚拟仿真实验教学资源</span>
        <div class="content">
          <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;本平台让学生可以在线学习理论和实操知识，虚拟交互练习，知识考核，虚实结合，辅助教学。本平台可以不受时间、空间、成本等因素的影响，无限期的使用所开发虚拟仿真实验教学资源, 学生可以不受时间空间限制，只要有网络的地方就可以动手做实验，重点解决实训条件不具备或实际运行困难,涉及高危或极端环境,高成本、高消耗、不可逆操作、大型综合训练等问题。</span>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="section test4">
      <div class="jianjie2">
        <span class="title">三、平台特色</span>
      </div>
    </div>

    <!-- Online Teaching Section -->
    <div class="section test5">
      <div class="jianjie2">
        <span class="title">四、"VR+云课堂"线上教学方案</span>
        <div class="content">
          <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;教师使用云平台上的虚拟仿真软件资源、结合教学PPT进行各个项目的VR教学,同时通过QQ群视频的形式进行在线直播授课,教师使用智慧树、雨课堂等工具对教学过程进行管控。</span>
        </div>
        <span class="subtitle">"VR+"云课堂资源</span>
      </div>
    </div>

    <!-- Resource List Section -->
    <div class="section test6">
      <div class="jianjie2">
        <span class="title">科 明 数 码 虚 拟 仿 真 教 学 资 源 明 细 表</span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.section { width: 100%; position: relative; }
.jianjie2 { position: relative; width: 1200px; margin: 0 auto; }

.test1 {
  background: url('https://www.keming365.com/images/科明虚拟仿真教学资源类型.png') center top no-repeat;
  background-color: #b5c9ff; height: 884px;
  .jianjie2 { padding-top: 120px; text-align: center; }
  .title {
    font-family: 'SourceHanSansCN', 'Microsoft YaHei', sans-serif;
    font-size: 52px; color: #fff; font-weight: bold; letter-spacing: 8px;
  }
  .subtitle {
    display: block; margin-top: 40px; font-family: 'Microsoft YaHei', sans-serif;
    font-size: 24px; color: #fff; margin-left: -60px;
  }
}

.test2 {
  background: url('https://www.keming365.com/images/科明VR教学资源.png') center top no-repeat;
  background-color: #b5c9ff; height: 751px;
  .jianjie2 { padding-top: 52px; }
  .title { font-size: 30px; color: #666; font-weight: bold; margin-left: 450px; }
  .content {
    margin-top: 80px; width: 543px; float: right;
    span { font-size: 24px; color: #666; display: block; line-height: 45.6px; }
  }
}

.test3 {
  background: url('https://www.keming365.com/images/虚拟仿真教学云平台.png') center top no-repeat;
  background-color: #b5c9ff; height: 751px;
  .jianjie2 { padding-top: 52px; }
  .title { font-size: 30px; color: #fff; font-weight: bold; margin-left: 430px; }
  .content {
    margin-top: 110px; width: 538px; float: left;
    span { font-size: 24px; color: #fff; display: block; line-height: 45px; }
  }
}

.test4 {
  background: url('https://www.keming365.com/images/云课堂线上教学解决方案.png') center top no-repeat;
  background-color: #b5c9ff; height: 994px;
  .jianjie2 { padding-top: 64px; }
  .title { font-size: 30px; color: #666; font-weight: bold; margin-left: 510px; }
}

.test5 {
  background: url('https://www.keming365.com/images/科明365VR教学云平台特色.png') center top no-repeat;
  background-color: #b5c9ff; height: 751px;
  .jianjie2 { padding-top: 94px; }
  .title { font-size: 30px; color: #666; font-weight: bold; margin-left: 350px; }
  .content {
    margin-top: 30px; width: 1200px; float: left;
    span { font-size: 24px; color: #666; display: block; line-height: 50px; }
  }
  .subtitle {
    display: block; margin-top: 200px; font-size: 30px;
    color: #666; font-weight: bold; margin-left: 450px;
  }
}

.test6 {
  background: url('https://www.keming365.com/images/科明虚拟仿真教学资源明细表.png') center top no-repeat;
  background-color: #b5c9ff; height: 11850px;
  .jianjie2 { padding-top: 94px; }
  .title { font-size: 30px; color: #666; font-weight: bold; margin-left: 315px; letter-spacing: 8px; }
}

@media(max-width:1200px) {
  .jianjie2 { width: 95%; }
  .test2 .title, .test3 .title, .test4 .title, .test5 .title, .test6 .title {
    margin-left: 0; text-align: center;
  }
  .test2 .content, .test3 .content { float: none; width: auto; }
}
</style>
