<template>
    <div class="requirement-list">
      <ul>
        <li v-for="(requirement, index) in filterRequirements" :key="index">
          <RequirementCard 
          :requirement="requirement" 
          :index="index"
          :cardInfo="props.cardInfo"
          />
        </li>
      </ul>
    </div>
  </template>
  
<script setup>
import axios from 'axios';

const props = defineProps({
  artifactId: Number,
  filters: Array,
  cardInfo: {
    model: String,
    version: String,
    artifactId: String
  }
})

const emit = defineEmits(['update-stats']);

const route = useRoute();
const config = useRuntimeConfig();

const requirements = ref([]);

const fetchRequirements = async () => {

  try {
    // const response = await fetch('/data/requirements.json');
    const response = await axios.get(
      config.public.apiPath + '/requirements/artifact/' 
      + props.artifactId + '/details'
    )
    // const data = await response.json();
    console.log("Requirements: ", response.data.requirements);
    requirements.value = response.data.requirements;

    await nextTick();
    scrollToRequirement();
  } catch (error) {
    console.error('There was a problem with your fetch operation:', error);
  }
};

const filterRequirements = computed(() => {
  if (!props.filters || props.filters.length === 0) {
    return requirements.value;
  }
  return requirements.value.filter(requirement => 
    requirement.categories.some(cat => props.filters.includes(cat))
  );
});

const scrollToRequirement = () => {
  const requirementIndex = route.query.requirementIndex;
  
  if (requirementIndex !== undefined) {
    setTimeout(() => {
      const requirementElement = document.querySelector(`.requirement-list li:nth-child(${Number(requirementIndex) + 1})`);
      
      if (requirementElement) {
        console.log("Scrolling to requirement:", requirementElement);
        requirementElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // requirementElement.classList.add('highlight-requirement-blink');
        // setTimeout(() => {
        //   requirementElement.classList.remove('highlight-requirement-blink');
        // }, 3000);
      }
    }, 100);
  }
};

watch(() => route.query.requirementIndex, (newIndex) => {
  if (newIndex !== undefined) {
    scrollToRequirement();
  }
});

function computeStats() {
  const total = filterRequirements.value.length;
  const met = filterRequirements.value.filter(req => !req.feedbacks || req.feedbacks.length === 0).length;

  emit('update-stats', { total, met });
}

onMounted(() => {
  fetchRequirements();
  computeStats();
});

watch(filterRequirements, computeStats, { deep: true });



</script>
  
<style scoped>
.requirement-list {
  padding: 20px;
  max-width: 500vb;
  overflow-y: auto;
}

.highlight-requirement-blink {
  animation: blink-highlight 3s;
}

@keyframes blink-highlight {
  0%, 100% { background-color: transparent; }
  20% { background-color: rgba(255, 235, 59, 0.7); }
  40% { background-color: transparent; }
  60% { background-color: rgba(255, 235, 59, 0.7); }
  80% { background-color: transparent; }
}

.highlight-requirement-prominent {
  animation: prominent-highlight 3s;
  position: relative;
  z-index: 1;
}

@keyframes prominent-highlight {
  0%, 100% { 
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(66, 133, 244, 0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: scale(1.02);
    box-shadow: 0 0 0 10px rgba(66, 133, 244, 0.4);
  }
  20%, 40%, 60%, 80% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(66, 133, 244, 0);
  }
}
</style>
  