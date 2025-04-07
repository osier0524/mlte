<template>
    <div class="requirement-card">
      <div class="requirement-header">
        <span class="requirement-id">{{ "Requirement " + (index + 1) }}</span> 
        <span class="requirement-category">{{ requirement.categories.join(", ") }}</span>
      </div>
      
      <div class="requirement-body">
        <p v-html="requirement.content"></p>
        <!-- <p v-if="requirement.description">{{ requirement.description }}</p> -->
        <!-- <p v-else>No description provided.</p> -->
      </div>

      <br />
      
      <div v-if="requirement.feedbacks">
        <QualityInspection :critiques="transformedCritiques" />
      </div>



      <br />

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
    },
    index: {
      type: Number,
      required: true
    }
  });

  const transformedCritiques = computed(() => {
    const result = {
      warnings: {},
      errors: {}
    }
    
    if (!props.requirement.feedbacks || !Array.isArray(props.requirement.feedbacks)) {
      return result;
    }

    for (const feedback of props.requirement.feedbacks) {
      const level = feedback.level;
      const target = level === 'warning' ? result.warnings : result.errors;

      for (const quality of feedback.qualities) {
        if (!target[quality.name]) {
          target[quality.name] = [];
        }
        target[quality.name].push(...quality.critiques);
      }
    }

    return result;
  })

  watchEffect(() => {
    console.log('Transformed critiques:', transformedCritiques.value);
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
  