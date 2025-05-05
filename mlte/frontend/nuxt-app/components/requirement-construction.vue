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
      <div class="quality-inspection" :class="{ 'is-loading': isLoading }">
        <div class="loading-bar" v-if="isLoading"></div>
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
          <div class="critique-section">
            <div class="critique-category warnings">
              <div class="critique-header">
                <Icon name="mdi:alert-circle-outline" class="icon-warning" />
                <h4>Warnings (Qualities do not meet the standard):</h4>
              </div>
              <div class="critique-content">
                <div v-if="critiques.warnings.length > 0" class="quality-tags">
                  <span v-for="(warning, index) in critiques.warnings" 
                        :key="index" 
                        class="quality-tag warning-tag">
                    {{ warning }}
                  </span>
                </div>
                <div v-else class="no-issues">No warnings found</div>
              </div>
            </div>
            
            <div class="critique-category errors">
              <div class="critique-header">
                <Icon name="mdi:close-circle-outline" class="icon-error" />
                <h4>Errors (Qualities are completely unsatisfactory):</h4>
              </div>
              <div class="critique-content">
                <div v-if="critiques.errors.length > 0" class="quality-tags">
                  <span v-for="(error, index) in critiques.errors" 
                        :key="index" 
                        class="quality-tag error-tag">
                    {{ error }}
                  </span>
                </div>
                <div v-else class="no-issues">No errors found</div>
              </div>
            </div>
          </div>


        </div>

        <div v-if="isExpanded" class="critiques-action">
          <UsaButton class="primary-button" @click="goToCritiques">
            See Detailed Critiques
          </UsaButton>
        </div>
  
        <span v-if="isExpanded" class="AIgeneratedtext" id="cautiontext"> The above evaluation is provided by AI. AI can make mistakes. </span>
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
        <option value="Functional">Functional</option>
        <option value="Non-Functional">Non-functional</option>
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
    card: {
      model: string
      version: string
      artifactId: string
    }
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

const emit = defineEmits(['delete', 'submit'])


const requirementId = ref<number | undefined>(undefined)

onMounted(() => {
  console.log('Requirement Index:', props.requirementIndex)
  const storageKey = 'requirement_id_' + props.artifactId + '_' + props.requirementIndex
  console.log('Storage key:', storageKey)
  const stored = localStorage.getItem(storageKey)
  console.log('Stored requirement ID:', stored)
  if (stored) {
      requirementId.value = Number(stored)
  }
  fetchCritiqueStats()
})

const config = useRuntimeConfig();
const router = useRouter();
const isExpanded = ref(false)
const isLoading = ref(false)

// TODO: handle update of requirement
async function saveRequirement() {
    const requestBody = {
        artifact_id: props.artifactId,
        card_index: props.requirementIndex,
        content: props.requirement.content,
    }
    if (props.artifactId === null) {
      toast.error('Please create an artifact first.')
      return
    }
    console.log('Saving requirement:', requestBody)
    
    const categories = [props.requirement.quality, props.requirement.category]
    const category_name = categories.sort()
    try {
      const storageKey = 'requirement_id_' + props.artifactId + '_' + props.requirementIndex
      const stored = localStorage.getItem(storageKey)
      let response = null
      let requirementChanged = false

      if (stored && stored !== 'undefined') {
        // Update existing requirement
        requirementId.value = Number(stored)
        // Compare with the existing requirement
        // if exists requirement
        if (requirementId.value) {
          const existingRequirement = await axios.get(
            config.public.apiPath + '/requirements/' + requirementId.value
          )
          if (existingRequirement.data.content !== requestBody.content) {
            console.log('Requirement content changed')
            requirementChanged = true
          }
        } else {
          console.log('No existing requirement found')
          requirementChanged = true
        }

        response = await axios.post(
          config.public.apiPath + '/requirements/' + requirementId.value,
          requestBody
        )
      }
      else {
        // Create new requirement
        console.log('Creating new requirement')
        response = await axios.post(
          config.public.apiPath + '/requirements',
          requestBody
        )
        requirementChanged = true
      }
      
      const returnedId = response.data.requirement_id
      requirementId.value = returnedId
      
      console.log('key:', storageKey)
      localStorage.setItem(storageKey, returnedId.toString())

      const category_body = {
        artifact_id: props.artifactId,
        card_index: props.requirementIndex,
        category_names: category_name,
      }
      console.log('Saving requirement categories:', category_body)
      const category_response = await axios.post(
        config.public.apiPath + '/requirements/' + requirementId.value + '/assign-categories',
        category_body
      )

      toast.success('Requirement saved successfully.\n Quality inspection is in progress.')

      if (requirementChanged) {
        critiqueRequirement()
      }
      emit('submit')
    }
    catch (error) {
      toast.error('Error saving requirement. Please try again.')
      console.error(error)
    }
}

async function critiqueRequirement() {
  isLoading.value = true
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
  finally {
    isLoading.value = false
  }
}

async function fetchCritiqueStats() {
  console.log('requirementId:', requirementId.value)
  if (!requirementId.value) {
    return
  }
  try{
    const response = await axios.get(
      config.public.apiPath + '/requirements/' + requirementId.value + '/critique-stats'
    )
    if (response.data === null) {
      return
    }
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
      model: props.card.model,
      version: props.card.version,
      artifactId: props.card.artifactId,
      intId: props.artifactId,
      requirementIndex: props.requirementIndex,
    },
  })
}

</script>

<style scoped>

.loading-bar {
  position: absolute;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #4a90e2, transparent);
  width: 100%;
  z-index: 10;
  background-size: 200% 100%;
  animation: shine 1.5s infinite linear;
}

@keyframes shine {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.quality-inspection {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  background-color: white;
}

.quality-inspection.is-loading {
  position: relative;
}

.quality-inspection.is-loading::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.7);
  z-index: 5;
  pointer-events: none;
}

.collapsable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background-color: #f8fafc;
  transition: background-color 0.2s ease;
}

.collapsable-header:hover {
  background-color: #f1f5f9;
}

.collapsable-title {
  font-weight: 600;
  color: #334155;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapsable-icons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.critique-category {
  margin-bottom: 16px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.critique-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  gap: 8px;
}

.warnings .critique-header {
  background-color: #fff8e1;
  border-left: 4px solid #f59e0b;
}

.errors .critique-header {
  background-color: #fee9e9;
  border-left: 4px solid #ef4444;
}

.critique-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.warnings .critique-header h4 {
  color: #b45309;
}

.errors .critique-header h4 {
  color: #e53e3e;
}

.icon-warning {
  color: #f59e0b;
  font-size: 1.2rem;
}

.icon-error {
  color: #ef4444;
  font-size: 1.2rem;
}

.critique-content {
  padding: 12px 16px;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-top: none;
}

.quality-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quality-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}

.warning-tag {
  background-color: #fff8e1;
  color: #b45309;
  border: 1px solid #ffc10726;
}

.error-tag {
  background-color: #fee9e9;
  color: #e53e3e;
  border: 1px solid #ff000017;
}

.no-issues {
  color: #64748b;
  font-style: italic;
  font-size: 0.9rem;
}

.warning, .error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.warning {
  background-color: #fff8e1;
  color: #b45309;
}

.error {
  background-color: #fee9e9;
  color: #e53e3e;
}

.icon-warning {
  color: #f59e0b;
}

.icon-error {
  color: #ef4444;
}

.collapsable-content {
  padding: 16px;
  background-color: #ffffff;
}

.warning-title, .error-title {
  font-weight: 600;
  color: #334155;
  font-size: 0.9rem;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-title {
  color: #b45309;
}

.error-title {
  color: #e53e3e;
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

#cautiontext {
  display: block;
  text-align: center;
  font-size: 0.75rem;
  color: #78350f;
  font-style: italic;
  padding: 10px 12px;
  margin-top: 16px;
  background-color: #efe8c7;
  border-radius: 6px;
}

.critiques-action {
  padding: 12px 16px;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
}

</style>
