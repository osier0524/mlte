<template>
  <div class="main-container">
    <div class="left-section">
      <h1 class="header">Individual Requirement Quality</h1>
      <CritiqueFilter 
        @update:selected="selectedLeftFilters = $event"
      />
      <RequirementList :filters="selectedLeftFilters"/>
    </div>
    <div class="right-section">
      <!-- Set of Requirement Quality -->
      <h1 class="header">Set of Requirement Quality</h1>
      <ProgressBar />
      <CritiqueFilter 
        @update:selected="selectedRightFilters = $event"
      />
      <QualityMeter 
        title="Complete"
        summary="Summary"
        :percentage="90"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { ref, watch } from 'vue';
import ProgressBar from 'primevue/progressbar';
export default {
  name: 'Critiques',

  setup() {
    const individualQualities = ref([
      {
        name: 'Necessary',
        isMet: false,
        critique: [
          { requirement: 'R1', critics: ['Critique 1', 'Critique 2'] },
          { requirement: 'R2', critics: ['Critique 2'] },
        ],
      },
      {
        name: 'Appropriate',
        isMet: false,
        critique: [
          { requirement: 'R3', critics: ['Critique 1'] },
        ],
      },
      {
        name: 'Unambiguous',
        isMet: true,
        critique: [],
      },
      {
        name: 'Complete',
        isMet: false,
        critique: [
          { requirement: 'R1', 
            critics: [
            'The term \'high level of accuracy\' is vague and lacks quantifiable targets. Without a specific accuracy percentage or error rate defined, it is challenging to measure or validate the requirement objectively during implementation and testing.',
            'The phrase \'major performance degradation\' is subjective and undefined. This requirement would be stronger with a clear definition or specific threshold that quantifies what constitutes major degradation, such as acceptable response times or error rates under specified conditions.'
            ] 
          },
        ],
      },
      {
        name: 'Singular',
        isMet: true,
        critique: [],
      },
      {
        name: 'Feasible',
        isMet: false,
        critique: [
          { requirement: 'R4', critics: ['Critique 1'] },
        ],
      },
      {
        name: 'Verifiable',
        isMet: true,
        critique: [],
      },
      {
        name: 'Correct',
        isMet: true,
        critique: [],
      },
      {
        name: 'Conforming',
        isMet: true,
        critique: [],
      }
    ]);

    const setQualities = ref([
      {
        name: 'Complete',
        isMet: false,
        critique: [
          { set: ['R1', 'R4'], critics: ['Critique 1', 'Critique 2'] },
          { set: ['R2', 'R3'], critics: ['Critique 2'] },
        ],
      },
      {
        name: 'Consistent',
        isMet: false,
        critique: [
          { set: ['R3', 'R6'], critics: ['Critique 1'] },
        ],
      },
      {
        name: 'Feasible',
        isMet: true,
        critique: [],
      },
      {
        name: 'Comprehensible',
        isMet: true,
        critique: [],
      },
      {
        name: 'Able to be Validated',
        isMet: true,
        critique: [],
      },
    ])

    const selectedLeftFilters = ref([]);
    const selectedRightFilters = ref([]);

    watch(selectedLeftFilters, (newVal) => {
      console.log('Selected Left Filters:', newVal);
    }, { deep: true });

    return {
      individualQualities,
      setQualities,
      selectedLeftFilters,
      selectedRightFilters,
    };
  },
  
};
</script>
  
<style scoped>
.main-container {
  display: flex;
  padding: 20px;
}

.left-section {
  width: 50%;
  height: 100vh;
  overflow-y: auto;
  padding: 10px;
  border-right: 2px solid #ddd;
}

.right-section {
  width: 50%;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.header {
  font-size: 1.5rem;
  text-align: center;
}
</style>
  