<template>
  <div class="about-page">
    <div class="hero">
      <h1>关于科明365VR教学云平台</h1>
      <p>国内领先的虚拟仿真教育在线学习平台，为高校提供一站式VR教学解决方案</p>
    </div>

    <div class="container">
      <div class="section">
        <h2>平台简介</h2>
        <p>科明365VR教学云平台由济南科明数码技术股份有限公司研发，是国内优质的虚拟仿真教育在线学习平台。平台涵盖科明数码数年来积累的高校机械类、土木类等数十个专业的1100多个虚拟仿真教学、实验资源。</p>
        <p>每一个有志学习的人，都可以在这里学习优质教学课程，与名师零交流。平台支持PC端、移动端，轻松开展虚拟仿真实验。</p>
      </div>

      <div class="stats">
        <div class="stat-card" v-for="s in stats" :key="s.label">
          <div class="num">{{ s.num }}</div>
          <div class="label">{{ s.label }}</div>
        </div>
      </div>

      <div class="section">
        <h2>核心优势</h2>
        <p><strong>丰富的VR资源</strong> — 涵盖机械工程、工程训练、力学、土木工程、装配式建筑、大学物理、能源动力、水利工程、生物工程、文化艺术、航海类、学前教育等12大学科。</p>
        <p><strong>前沿技术</strong> — 采用VR虚拟现实技术，打造沉浸式教学体验，支持3D仿真、在线实验、虚拟实训。</p>
        <p><strong>教学创新</strong> — 支持线上-线下-混合式金课、一流课程、虚拟仿真项目建设，助力高校教学改革。</p>
      </div>

      <div class="contact">
        <h3>联系我们</h3>
        <p>公司：济南科明数码技术股份有限公司</p>
        <p>电话：4000-927-928</p>
        <p>官网：www.keming365.com</p>
        <p>地址：山东省济南市高新区</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const stats = [
  { num: '12+', label: '学科门类' },
  { num: '1100+', label: '教学资源' },
  { num: '300+', label: '合作院校' },
  { num: '100万+', label: '服务用户' },
]
</script>

<style lang="scss" scoped>
.hero {
  background: linear-gradient(135deg, #1a237e, #3949ab);
  color: #fff; text-align: center; padding: 80px 20px;
  h1 { font-size: 36px; margin-bottom: 12px; }
  p { font-size: 16px; opacity: .85; max-width: 600px; margin: 0 auto; }
}
.container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
.section {
  margin-bottom: 40px;
  h2 {
    font-size: 22px; color: #1a237e; margin-bottom: 16px;
    padding-bottom: 8px; border-bottom: 2px solid #eef0f7;
  }
  p { font-size: 14px; color: #555; line-height: 1.8; margin-bottom: 12px; }
}
.stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 40px 0;
}
.stat-card {
  background: #fff; border-radius: 12px; padding: 30px;
  text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.06);
  .num { font-size: 32px; font-weight: 700; color: #1a237e; }
  .label { font-size: 13px; color: #999; margin-top: 6px; }
}
.contact {
  background: #fff; border-radius: 12px; padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
  h3 { font-size: 16px; color: #1a237e; margin-bottom: 12px; }
  p { font-size: 14px; color: #555; line-height: 2; }
}

@media(max-width:768px) {
  .stats { grid-template-columns: repeat(2, 1fr); }
  .hero h1 { font-size: 26px; }
}
</style>
