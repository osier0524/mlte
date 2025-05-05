<template>
  <div class="requirement-card" 
      :class="{ 
        'has-issues': hasQualityIssues,
        'highlight-card': isHighlighted
    }">
    <div class="card-header">
      <div class="requirement-id">{{ "Requirement " + (index + 1) }}</div>
      <div class="category-chips">
        <span v-for="(category, cIndex) in requirement.categories" 
              :key="cIndex" 
              class="category-chip">
          {{ category }}
        </span>
      </div>
    </div>
    
    <div class="card-body">
      <div class="requirement-content" v-html="requirement.content"></div>
    </div>
    
    <!-- Quality Inspection Section -->
    <div v-if="requirement.feedbacks" class="quality-inspection-wrapper">
      <QualityInspection :critiques="transformedCritiques" />
    </div>
    
    <div class="card-actions">
      <UsaButton class="secondary-button" @click="goToNCard">
        Edit
      </UsaButton>
    </div>

  </div>
</template>

<script setup>

const route = useRoute();
const router = useRouter();
const isHighlighted = ref(false);

const props = defineProps({
  requirement: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  cardInfo: {
    model: String,
    version: String,
    artifactId: String
  }
});

onMounted(() => {
  checkHighlight();
})

watch(() => route.query.requirementIndex, () => {
  checkHighlight();
});

const transformedCritiques = computed(() => {
  const result = {
    warnings: {},
    errors: {}
  };
  
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
});

const hasQualityIssues = computed(() => {
  return Object.keys(transformedCritiques.value.warnings).length > 0 || 
         Object.keys(transformedCritiques.value.errors).length > 0;
});

// This function would be implemented to navigate to the edit page
const goToNCard = () => {
  // Your navigation logic here
  router.push({
    path: '/negotiation-card',
    query: {
      model: props.cardInfo.model,
      version: props.cardInfo.version,
      artifactId: props.cardInfo.artifactId,
      requirementIndex: route.query.requirementIndex,
    },
  })
};

function checkHighlight() {
  const requirementIndex = route.query.requirementIndex;
  
  if (requirementIndex !== undefined && Number(requirementIndex) === props.index) {
    isHighlighted.value = true;

    setTimeout(() => {
      const element = document.querySelector('.highlight-card');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);

    setTimeout(() => {
      isHighlighted.value = false;
    }, 3000);
  }
}

</script>

<style scoped>
.requirement-card {
  background-color: white;
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  overflow: hidden;
  transition: box-shadow 0.3s ease, transform 0.2s ease;
}

.requirement-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.has-issues {
  border-left: 4px solid #FFC107;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background-color: #f7f9fc;
  border-bottom: 1px solid #edf2f7;
}

.requirement-id {
  font-weight: 600;
  color: #4361ee;
  font-size: 0.95rem;
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}

.category-chip {
  background-color: #e6effd;
  color: #3182ce;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.card-body {
  padding: 16px;
}

.requirement-content {
  color: #2d3748;
  font-size: 0.95rem;
  line-height: 1.6;
}

.quality-inspection-wrapper {
  padding: 0 16px 16px;
}

.card-actions {
  padding: 12px 16px;
  border-top: 1px solid #edf2f7;
  display: flex;
  justify-content: flex-end;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s ease;
}


.highlight-card {
  animation: card-pulse 3s;
  position: relative;
  z-index: 10;
}

@keyframes card-pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 2px solid transparent;
  }
  10%, 30%, 50%, 70%, 90% {
    box-shadow: 0 0 20px 5px rgba(255, 193, 7, 0.6);
    border: 2px solid #FFC107;
  }
  20%, 40%, 60%, 80% {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 2px solid transparent;
  }
}
</style>