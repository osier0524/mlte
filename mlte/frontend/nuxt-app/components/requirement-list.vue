<template>
    <div class="requirement-list">
      <ul>
        <li v-for="(requirement, index) in filterRequirements" :key="index">
          <RequirementCard 
          :requirement="requirement" 
          :index="index"
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
  })
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
      console.log(response.data.requirements);
      requirements.value = response.data.requirements;
    } catch (error) {
      console.error('There was a problem with your fetch operation:', error);
    }
  };

  onMounted(fetchRequirements);

  const filterRequirements = computed(() => {
    if (!props.filters || props.filters.length === 0) {
      return requirements.value;
    }
    return requirements.value.filter(requirement => 
      requirement.category.some(cat => props.filters.includes(cat))
    );
  });

  watchEffect(() => {
    console.log('Filtered requirements:', filterRequirements.value);
  });
  

  </script>
  
  <style scoped>
  .requirement-list {
    padding: 20px;
    max-width: 500vb;
    overflow-y: auto;
  }
  </style>
  