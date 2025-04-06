<template>
    <div>
      <h3 class="no-margin-sub-header">
        Requirement {{ requirementIndex + 1 }}
      </h3>
      <p class="input-group" style="padding-top: 10px; padding-bottom: 10px">
        <b>Scenario for {{ requirement.quality }}: </b>
        {{ requirement.content }}
      </p>
      <br />
      <div class="quality-inspection">
        <div class="collapsable-header" @click="isExpanded = !isExpanded">
          <span class="collapsable-title">
            {{ isExpanded ? '▼' : '▶' }} Requirement Quality Inspection
          </span>
          <span class="collapsable-icons">
            <span class="warning">
              <Icon name="mdi:alert-circle-outline" class="icon-warning" />
              {{ critiques.warnings.length }}
            </span>
            <span class="error">
              <Icon name="mdi:close-circle-outline" class="icon-error" />
              {{ critiques.errors.length }}
            </span>
          </span>
        </div>
  
        <div v-if="isExpanded" class="collapsable-content">
          <p class="warning-title">Warnings:</p>
          <p class="warning-list">{{ critiques.warnings.join(', ') }}</p>
          <br />
          <p class="error-title">Errors:</p>
          <p class="error-list">{{ critiques.errors.join(', ') }}</p>
          <br />
          <UsaButton class="primary-button" @click="goToCritiques">
            See Detailed Critiques
          </UsaButton>
        </div>
  
        <span class="AIgeneratedtext" id="cautiontext"> The above evaluation is provided by AI. AI can make mistakes. </span>
      </div>
  
      <UsaTextInput v-model="requirement.quality">
        <template #label>
          System Quality
          <InfoIcon>
            System property by which the model will be evaluated <br />
            (e.g., Accuracy, Performance, Robustness, Fairness, Resource
            Consumption). <br /><br />
            <i>Example: Response time.</i>
          </InfoIcon>
        </template>
      </UsaTextInput>
  
      <UsaSelect v-model="requirement.category">
        <template #label>
          Requirement Category
          <InfoIcon>
            Classify the requirement as either functional or non-functional. <br /><br />
            <i>Example: Non-functional – Response time.</i>
          </InfoIcon>
        </template>
        <option value="">Please select</option>
        <option value="functional">Functional</option>
        <option value="non-functional">Non-functional</option>
      </UsaSelect>
  
      <UsaTextInput v-model="requirement.content">
        <template #label> Requirement Content </template>
      </UsaTextInput>

      <SaveButton class="margin-button" @click="saveRequirement">
        Save Requirement
      </SaveButton>
  
      <DeleteButton class="margin-button" @click="$emit('delete', requirementIndex)">
        Delete Requirement
      </DeleteButton>

      <hr />
    </div>
</template>
  
<script setup lang="ts">
import axios from 'axios';

const props = defineProps<{
    artifactId: any
    requirement: any
    requirementIndex: number
}>()

interface CritiqueStats {
  warnings: string[];
  errors: string[];
}

const critiques = ref<CritiqueStats>({
  warnings: [],
  errors: []
})

defineEmits(['delete'])

const requirementId = ref<number | undefined>(undefined)

onMounted(() => {
  const stored = localStorage.getItem('requirement_id')
    if (stored) {
        requirementId.value = Number(stored)
    }
})

const config = useRuntimeConfig();
const router = useRouter();
const isExpanded = ref(false)

// TODO: handle update of requirement
async function saveRequirement() {
    const requestBody = {
        artifact_id: props.artifactId,
        content: props.requirement.content,
    }
    if (props.artifactId === null) {
      alert('Please save the artifact first.')
      return
    }
    console.log('Saving requirement:', requestBody)
    try {
      const reponse = await axios.post(
        config.public.apiPath + '/requirements',
        requestBody
      )
      const returnedId = reponse.data.requirement_id
      requirementId.value = returnedId
      localStorage.setItem('requirement_id', returnedId.toString())
      alert('Requirement saved successfully!')
    }
    catch (error) {
      alert('Error saving requirement. Please try again.')
      console.error(error)
    }
    critiqueRequirement()
}

async function critiqueRequirement() {
  try {
    const response = await axios.post(
      config.public.apiPath + '/critiques?artifact_id=' + props.artifactId
      + '&requirement_id=' + requirementId.value
    )
    console.log('Critique received:', response.data)
    critiques.value.warnings = response.data.warnings
    critiques.value.errors = response.data.errors
  } catch (error) {
    console.error('Error fetching critique:', error)
  }
}

function goToCritiques() {
  router.push({
    path: '/critiques',
    query: {
      artifactId: props.artifactId,
    },
  })
}

</script>

<style scoped>
.quality-inspection {
  border: 1px solid #000;
  border-radius: 5px;
  padding: 10px; 
}

.collapsable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.collapsable-title {
  font-weight: bold;
}

.collapsable-icons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning, .error {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-warning {
  color: gold;
  font-size: 20px;
}

.icon-error {
  color: red;
  font-size: 20px;
}

.collapsable-content {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.warning-title,
.error-title {
  font-weight: bold;
}

.warning-list {
  margin-left: 10px;
  color: rgb(193, 156, 9)}

.error-list {
  margin-left: 10px;
  color: red;
}

.AIgeneratedtext{
  background-color: #efe8c7;
  font-style: italic;
}

#cautiontext{
  font-size: 12px;
  font-style: italic;
  text-align: center;
}

</style>
