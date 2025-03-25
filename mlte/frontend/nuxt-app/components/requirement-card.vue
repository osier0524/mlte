<template>
    <div class="requirement-card">
      <div class="requirement-header">
        <span class="requirement-id">{{ "Requirement " + requirement.id }}</span> 
        <span class="requirement-category">{{ requirement.category.join(", ") }}</span>
      </div>
      
      <div class="requirement-body">
        <p v-html="requirement.description"></p>
        <!-- <p v-if="requirement.description">{{ requirement.description }}</p> -->
        <!-- <p v-else>No description provided.</p> -->
      </div>

      <br />
      
      <div v-if="requirement.feedback">
        <QualityInspection :critiques="requirement.feedback" />
      </div>



      <br />

      <!-- Warnings Section -->
      <!-- <div v-if="requirement.warnings && requirement.warnings.length" class="requirement-warnings">
        <span class="warnings-title">Warnings {{ requirement.warnings.length }}</span>
        <ul>
          <li v-for="(warning, index) in requirement.warnings" :key="'warn-' + index">
            {{ index + 1 }}. {{ warning }}
          </li>
        </ul>
      </div> -->

      <!-- Errors Section -->
      <!-- <div v-if="requirement.errors && requirement.errors.length" class="requirement-errors">
        <span class="errors-title">Errors {{ requirement.errors.length }}</span>
        <ul>
          <li v-for="(error, index) in requirement.errors" :key="'err-' + index">
            {{ index + 1 }}. {{ error }}
          </li>
        </ul>
      </div> -->

      <!-- Edit Button -->
      <UsaButton class="secondary-button" @click="goToNCard">
        Edit
      </UsaButton>
    </div>
  </template>
  
  <script setup>
  
  const props = defineProps({
    requirement: {
      type: Object,
      required: true
    }
  });

  </script>
  
  <style scoped>
  .requirement-card {
    border: 1px solid ;
    padding: 10px;
    margin-bottom: 15px;
    background-color: #fff;
  }
  
  .requirement-header {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  .requirement-id {
    color: #007BFF;
  }
  
  .requirement-title {
    font-size: 16px;
    color: #333;
  }
  
  .requirement-body {
    font-size: 16px;
  }
  
  .requirement-warnings {
  margin-top: 10px;
  font-size: 14px;
  color: #d39e00;
  }

  .warnings-title {
    font-weight: bold;
    color: #d39e00;
  }

  .requirement-errors {
    margin-top: 10px;
    font-size: 14px;
    color: #dc3545;
  }

  .errors-title {
    font-weight: bold;
    color: #dc3545;
  }

  ul {
    padding-left: 20px;
    margin: 5px 0;
  }

  li {
    list-style-type: none;
  }
  </style>
  