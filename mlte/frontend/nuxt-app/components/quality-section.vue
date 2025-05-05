<template>
    <div class="quality-section">
      <h3>{{ title }}</h3>
      <ul>
        <li v-for="(quality, index) in qualities" :key="index" :class="{ fail: !quality.isMet }">
          <strong>{{ quality.name }}</strong>: 
          <span>{{ quality.isMet ? 'Pass' : 'Fail' }}</span>
          <div v-if="!quality.isMet" class="critique">
            <p>{{ quality.critique }}</p>
          </div>
        </li>
      </ul>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue';
  
  const props = defineProps({
    title: String,  // 标题，例如 "Individual Requirement Quality"
    qualities: Array // 各个质量指标的数组
  });
  </script>
  
  <style scoped>
  .quality-section {
    margin-bottom: 20px;
  }
  
  .fail {
    color: red;
  }
  
  .critique {
    margin-top: 10px;
    font-style: italic;
    color: #f00;
  }
  </style>
  