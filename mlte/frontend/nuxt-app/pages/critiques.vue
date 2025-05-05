<template>
  <div class="critiques-container">
    <div class="left-section">
      <div class="section-header">
        <h1 class="header-title">Individual Requirement Quality</h1>
        <div class="header-badge">{{ stats.metRequirementsCount }}/{{ stats.totalRequirementsCount }}</div>
      </div>
      
      <div class="filter-section">
        <CritiqueFilter
          v-model="selectedLeftFilters"
          @update:selected="selectedLeftFilters = $event" 
        />
      </div>
      
      <RequirementList 
        :filters="selectedLeftFilters"
        :artifactId="artifactId"
        :cardInfo="cardInfo"
        @update-stats="updateStats"
      />
    </div>
    
    <div class="right-section">
      <div class="section-header">
        <h1 class="header-title">Set of Requirement Quality</h1>
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ overallPercentage }}%</div>
            <div class="stat-label">Overall Completion</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">{{ metQualitiesCount }}/{{ totalQualitiesCount }}</div>
            <div class="stat-label">Standards Met</div>
          </div>
        </div>
      </div>
      
      <div class="progress-overview">
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: `${overallPercentage}%`, backgroundColor: getStatusColor(overallPercentage) }"></div>
        </div>
      </div>
      
      <div class="filter-section">
        <CritiqueFilter 
          v-model="selectedRightFilters"
          @update:selected="selectedRightFilters = $event" />
      </div>
      
      <!-- <div class="quality-meters">
        <QualityMeter 
          v-for="quality in setQualities"
          :key="quality.name"
          :title="quality.name"
          :summary="quality.summary"
          :percentage="quality.percentage"
          :critiques="quality.critique"
        />
      </div> -->

      <div class="quality-meters">
        <div v-if="isSetCritiqueLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <div class="loading-text">Generating quality analysis...</div>
        </div>
        <template v-else>
          <QualityMeter 
            v-for="quality in setQualities"
            :key="quality.name"
            :title="quality.name"
            :summary="quality.summary"
            :percentage="quality.percentage"
            :critiques="quality.critique"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios';

const config = useRuntimeConfig();
const route = useRoute();
const artifactId = Number(route.query.intId);

const cardInfo = {
  model: route.query.model,
  version: route.query.version,
  artifactId: route.query.artifactId,
}

const setQualities = ref([
  {
    name: 'Complete',
    isMet: false,
    summary: 'The requirement set is missing critical functionality needed for the system to meet its objectives. There are gaps in coverage for user authentication flows and error handling scenarios.',
    critique: [
      { set: ['R1', 'R4'], critics: ['Missing complete description of user authentication flows', 'Not covering all possible error handling scenarios'] },
      { set: ['R2', 'R3'], critics: ['System boundary conditions not fully defined'] },
    ],
    percentage: 50,
  },
  {
    name: 'Consistent',
    isMet: false,
    summary: 'These requirements are not consistent with each other. The requirement R1 states that the system should be able to handle 1000 concurrent users, while R2 states that it should be able to handle 2000 concurrent users. This inconsistency can lead to confusion and misinterpretation during implementation.',
    critique: [
      { set: ['R1', 'R2'], critics: ['Inconsistent requirements for concurrent users between R1 and R2'] },
      { set: ['R3', 'R6'], critics: ['Conflict in data retention periods between R3 and R6'] },
    ],
    percentage: 50,
  },
  {
    name: 'Feasible',
    isMet: true,
    summary: 'These requirements are feasible and can be implemented within the given constraints. The requirement R1 states that the system should be able to handle 1000 concurrent users, while R2 states that it should be able to handle 2000 concurrent users. This is feasible as the system has the necessary resources and infrastructure to support these requirements.',
    critique: [],
    percentage: 100,
  },
  {
    name: 'Comprehensible',
    isMet: true,
    summary: 'These requirements are comprehensible and can be easily understood by all stakeholders. The requirement R1 states that the system should be able to handle 1000 concurrent users, while R2 states that it should be able to handle 2000 concurrent users. This is comprehensible as the requirements are clear and unambiguous.',
    critique: [],
    percentage: 100,
  },
  {
    name: 'Able to be Validated',
    isMet: true,
    summary: 'These requirements are able to be validated and can be tested to ensure they meet the specified criteria. The requirement R1 states that the system should be able to handle 1000 concurrent users, while R2 states that it should be able to handle 2000 concurrent users. This is able to be validated as the requirements can be tested against the system\'s performance metrics.',
    critique: [],
    percentage: 100,
  },
]);

const isSetCritiqueLoading = ref(false);

const selectedLeftFilters = ref([]);
const selectedRightFilters = ref([]);

watchEffect(() => {
  console.log('Selected Left Filters:', selectedLeftFilters.value);
});

watchEffect(() => {
  console.log('Selected Right Filters:', selectedRightFilters.value);
});

onMounted(() => {
  console.log('Artifact ID:', artifactId);
  setTimeout(() => {
    checkAndMaybeCritique();
  }, 100)
  fetchQualities();
});

// Computed values for summary statistics
const stats = reactive({
  metRequirementsCount: 0,
  totalRequirementsCount: 0,
});

function updateStats({ total, met }) {
  stats.totalRequirementsCount = total;
  stats.metRequirementsCount = met;
}

const metQualitiesCount = computed(() => setQualities.value.filter(q => q.isMet).length);
const totalQualitiesCount = computed(() => setQualities.value.length);

const overallPercentage = computed(() => {
  const total = setQualities.value.reduce((sum, quality) => sum + quality.percentage, 0);
  return Math.round(total / setQualities.value.length);
});


const versionMap = ref(getVersionMap());

// Check if the requirements set in database has been updated
// If updated, critize them
async function checkAndMaybeCritique() {
  const filterKey = generateFilterKey(selectedRightFilters.value);
  const cacheKey = `${artifactId}:${filterKey}`;
  let filter_criteria = '';
  if (selectedRightFilters.value.length === 0) {
    filter_criteria = 'All';
  } else {
    // sort and join
    filter_criteria = selectedRightFilters.value.sort().join(',');
  }
  const res = await axios.post(
    `${config.public.apiPath}/critiques/set-critique/version`,
    {
      artifact_id: artifactId,
      filter_criteria: filter_criteria,
    }
  )
  console.log('Version response:', res.data);
  const version = res.data.version;
  console.log('Version:', version);
  console.log('Old Version:', versionMap.value.get(cacheKey));

  if (versionMap.value.get(cacheKey) !== version) {
    // trigger set critique
    isSetCritiqueLoading.value = true;
    try {
      const response = await axios.post(
        `${config.public.apiPath}/critiques/set-critique`,
        {
          artifact_id: artifactId,
          filter_criteria: filter_criteria,
        }
      );
      versionMap.value.set(cacheKey, version);
      saveVersionMap(versionMap.value);      
    } catch (error) {
      console.error('Error fetching critiques:', error);
    } finally {
      isSetCritiqueLoading.value = false;
    }
  } else {
    console.log('Version unchanged, no need to regnerate critiques.');
  }
}

// fetch quality from the server
const fetchQualities = async () => {
  try {
    let filter_criteria = '';
    if (selectedRightFilters.value.length === 0) {
      filter_criteria = 'All';
    } else {
      // sort and join
      filter_criteria = selectedRightFilters.value.sort().join(',');
    }
    console.log('filter_criteria:', filter_criteria);
    const response = await axios.get(
      `${config.public.apiPath}/artifacts/${artifactId}/set-critique`,
      {
        params: {
          filter_criteria: filter_criteria,
        },
      }
    );
    console.log('Fetched qualities:', response.data);
    console.log('Fetched qualities:', response.data.qualities);
    if (response.data.qualities) {
      setQualities.value = response.data.qualities.map((q) => ({
        ...q,
        isMet: q.percentage === 100,
      }));
    } else {
      setQualities.value = [];
    }
  } catch (error) {
    console.error('Error fetching qualities:', error);
  } finally {
    isSetCritiqueLoading.value = false;
  }
};

// Fetch critiques when selected filters change
watch(selectedRightFilters, (newFilters) => {
  console.log('Selected Right Filters changed:', newFilters);
  setTimeout(() => {
    checkAndMaybeCritique();
  }, 100);
  fetchQualities();
}, { deep: true });


// Helper functions
const getStatusColor = (percentage) => {
  if (percentage >= 90) return '#4CAF50'; // Green
  if (percentage >= 70) return '#8BC34A'; // Light Green
  if (percentage >= 50) return '#FFC107'; // Amber
  if (percentage >= 30) return '#FF9800'; // Orange
  return '#F44336'; // Red
};

function getVersionMap() {
  const raw = localStorage.getItem('versionMap');
  if (!raw) return new Map();
  return new Map(JSON.parse(raw));
}

function saveVersionMap (map) {
  localStorage.setItem('versionMap', JSON.stringify([...map.entries()]));
}

function generateFilterKey(filterArray) {
  return [...filterArray].sort().join(',');
}
</script>

<style scoped>
.critiques-container {
  display: flex;
  min-height: 100vh;
  background-color: #f7f9fc;
}

.left-section, .right-section {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.left-section {
  border-right: 1px solid #e0e0e0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-badge {
  background-color: #e0e0e0;
  color: #333;
  padding: 4px 12px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 0.9rem;
}

.overview-stats {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 12px;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 0.75rem;
  color: #666;
  white-space: nowrap;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background-color: #e0e0e0;
}

.progress-overview {
  margin-bottom: 24px;
}

.progress-bar-container {
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  transition: width 0.5s ease-in-out;
}

.filter-section {
  margin-bottom: 24px;
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.quality-meters {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  min-height: 200px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-text {
  color: #666;
  font-size: 0.9rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>