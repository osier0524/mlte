<template>
    <div class="requirement-list">
      <ul>
        <li v-for="(requirement, index) in filterRequirements" :key="index">
          <RequirementCard :requirement="requirement" />
        </li>
      </ul>
    </div>
  </template>
  
  <script setup>

  const props = defineProps({
    filters: Array,
  })
  
  const requirements = ref([]);
  
  const fetchRequirements = async () => {
    // const response = await fetch('/api/requirements');
    // const data = await response.json();
    // requirements.value = data;
    // mock data
    try {
      const response = await fetch('/data/requirements.json');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      requirements.value = data;
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
  

  </script>
  
  <style scoped>
  .requirement-list {
    padding: 20px;
    max-width: 500vb;
    overflow-y: auto;
  }
  </style>
  