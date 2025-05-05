<template>
  <br />
  <!-- API call -->
  <div class="chatgptcall">
    <p>
      Explainability refers to the ability to describe the decisions of a machine learning model in a way that is understandable to the end users.
      <span class="AIgeneratedtext">{{ response }} </span>
    </p>
  </div>
  <br />

<!-- List of stakeholders-->
  <div v-for="(field, fieldIndex) in dataItem.fields" :key="fieldIndex">
     <h3 class="no-margin-sub-header">
      <b>Stakeholder or Recipient {{ fieldIndex + 1 }} </b> 

         <div class="info-container">
            <span class="info-icon">i</span>
            <div class="tooltip"> Select the person or party for whom you are writing the requirement..</div>
           </div>
     </h3>
  <!-- Q1) Select the generated Stakeholders List -->
  <USelect
    placeholder="Select an option..."
    icon="i-heroicons-magnifying-glass-20-solid"
    v-model="stakeholder"
    :options="stakeholder_list"
    @change="onStakeholderChange" 
  />
  <!-- Conditionally show input field for 'Other' -->
  <br />
  <div v-if="showOtherInput">
    <label for="otherInput"><b>*Specify Other Stakeholder</b> </label>
    <UInput v-model="OtherStakeholder" style="width: 300px;" />
    <br />
  </div>

  <!-- Q2)generate a list of purposes based on the stakeholder previously selected -->
  <label><b>Purposes for Explainability</b></label>


    <div class="info-container">
      <span class="info-icon">i</span>
      <div class="tooltip"> Select the purposes for explainability related to the previously selected stakeholder.</div>
    </div>
  <USelectMenu
    multiple placeholder="Select an option..."
    icon="i-heroicons-magnifying-glass-20-solid"
    v-model="purpose"
    :options="purpose_list"
  />
  <br/>

  <label><b>Type of Explanation</b></label>

   <div class="info-container">
      <span class="info-icon">i</span>
      <div class="tooltip">{{ Q3_response }}</div>
    </div>

   <USelectMenu
    multiple placeholder="Select an option..."
    icon="i-heroicons-magnifying-glass-20-solid"
    v-model="typeofExplanation"
    :options="['Global Explanation', 'Local Explanation', 'Data Disclosure', 'Other']"
  />
  <br/>



  <label><b>Language Level</b></label>
  <div class="info-container">
  <span class="info-icon">e</span>
  <div class="tooltip"> {{ Q4_response }}</div>
  </div>

  <UInput v-model="language_expectations" />

  <br/>
  <label><b>Test Plan</b></label>
    <div class="info-container">
  <span class="info-icon">e</span>
  <div class="tooltip"> {{ Q5_response }}</div>
  </div>
          
  <UInput v-model="test_plan" />
  <br/>

   <!-- Dynamic Sentence -->
   <p class="input-group" style="padding-top: 10px; padding-bottom: 10px">

  <b>Scenario for Explainability: </b>For the stakeholder [{{ selectedStakeholderLabel }}], the purposes for explainability are [{{ selectedPurposeLabels }}]. 
    The model needs to have a [{{ typeofExplanation }}]. The explanations should be delivered at a language level targeted for [{{ language_expectations }}]. 
    The test plan to fulfill explainability expectations are [{{ test_plan }}].
  </p>
<br/>


      <DeleteButton class="margin-button" @click="deleteField(dataItemIndex, fieldIndex)">
         Delete Requirement
      </DeleteButton>
        <hr />
      </div>

      <AddButton class="margin-button" @click="addField(dataItemIndex)">
            Add Requirement
      </AddButton>
        



</template>

<script lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { openai } from '~/composables/openai';

export default {
  name: 'InferenceLatencyForm',
  props: {
    MLTask: { required: true },
    usageContext: { required: true },
  },
  setup(props) {
    const response = ref('');
    const Q3_response = ref('');
    const Q4_response = ref('');
    const Q5_response = ref('');
    const stakeholder = ref('');
    
    const stakeholder_list = ref([]);
    const purpose = ref([]);
    const purpose_list = ref([]);
    const typeofExplanation = ref([]);
    const OtherStakeholder = ref('');
    const showOtherInput = ref(false);
    const language_expectations = ref('');
    const test_plan = ref('');

    const handleSelection = () => {
      showOtherInput.value = stakeholder.value === 'stakeholder_other';
    };

    // get the value of the stakeholder selected 

    const selectedStakeholderLabel = computed(() => {
      const selected = stakeholder_list.value.find(
        (option) => option.value === stakeholder.value
      );
      return selected ? selected.label : stakeholder.value;
    });

    // extract the val of the purposes selected:
    const selectedPurposeLabels = computed(() => {
      return purpose.value.map((selectedPurpose) => selectedPurpose.label).join(', ');
      });



    watch(stakeholder, handleSelection);

    // Table Headers and Rows
    const dataModalHeaders = ref([
      { text: 'Field Name', value: 'name' },
      { text: 'Description', value: 'description' },
      { text: 'Type', value: 'type' },
      { text: 'Expected Values', value: 'expected_values' },
      { text: 'Missing Values', value: 'missing_values' },
      { text: 'Special Values', value: 'special_values' },
    ]);

    const dataModalRows = ref([]);

    // Data Schema Structure
    const dataItem = ref({
      fields: [
        {
          name: '',
          description: '',
          type: '',
          expected_values: '',
          missing_values: '',
          special_values: '',
        },
      ],
    });

    // Add Field Functionality
    const addField = () => {
      dataItem.value.fields.push({
        name: '',
        description: '',
        type: '',
        expected_values: '',
        missing_values: '',
        special_values: '',
      });
    };

    // Delete Field Functionality
    function deleteField(fieldIndex) {
      if (confirm("Are you sure you want to delete this field?")) {
      dataItem.value.fields.splice(fieldIndex, 1);
      }
      }

    const getChatResponse = async () => {
      const { chat } = openai();
      try {
        const messages = [
          {
            role: 'system',
            content: 'You are a specialized data scientist with knowledge in both software engineering and data science. Offer thoughtful insights.',
          },
          {
            role: 'user',
            content: `Write a concise sentence explaining a potential consequence of neglecting proper explainability in the context of ${props.MLTask} and ${props.usageContext} for a non-technical stakeholder of the product. Instead of mentioning trust as a requirement, provide an example of what that means.`,
          },
        ];
        const chatResponse = await chat(messages, 'gpt-3.5-turbo');
        response.value = chatResponse.split('\n\n')[0];
      } catch (error) {
        console.error('Error fetching chat response:', error);
      }
    };

    const GetStakeholders = async () => {
      const { chat } = openai();
      try {
        const messages = [
          {
            role: 'system',
            content: 'You are a product manager with experience in managing AI products.',
          },
          {
            role: 'user',
            content: `Provide a list of specific potential technical and non-technical stakeholders for a ${props.MLTask} model and the context use is ${props.usageContext}. Provide an unnumbered list of stakeholders without any explanations`,
          },
        ];

        const chatStakeholders = await chat(messages, 'gpt-3.5-turbo');
        const stakeholdersArray = chatStakeholders
          .split('\n')
          .filter(stakeholder => stakeholder.trim() !== '')
          .map((stakeholder, index) => ({
            label: stakeholder.replace(/^-/, '').trim(),
            value: `stakeholder_${index}`,
          }));

        stakeholder_list.value = stakeholdersArray;
        stakeholder_list.value.push({ label: 'Other', value: 'stakeholder_other' });
      } catch (error) {
        console.error('Error fetching chat response for stakeholders:', error);
      }
    };



  // Fetch purposes dynamically based on stakeholder
  const GetPurpose = async (selectedStakeholder) => {
      const { chat } = openai();
      try {
        const messages = [
          {
            role: 'system',
            content: 'You are a product manager with experience in managing AI products.',
          },
          {
            role: 'user',
            content: `Generate purposes for explainability for a ${selectedStakeholder.value} in the context of ${props.MLTask} and ${props.usageContext}. Provide an unnumbered list. Do not mention trust without explaining what that means in this context.
            Provide brief sentences of around 15 words.  `,
          },
        ];

        const chatPurpose = await chat(messages, 'gpt-3.5-turbo');
        const PurposeArray = chatPurpose
          .split('\n')
          .filter((purpose) => purpose.trim() !== '')
          .map((purpose, index) => ({
            label: purpose.replace(/^-/, '').trim(),
            value: `purpose_${index}`,
          }));

        purpose_list.value = PurposeArray;
        purpose_list.value.push({ label: 'Other', value: 'purpose_other' });
      } catch (error) {
        console.error('Error fetching chat response for purpose:', error);
      }
    };


    // watching when the stakeholder has been selected:
    // Watch for stakeholder selection changes
    const onStakeholderChange = (newStakeholder) => {
      if (newStakeholder === 'stakeholder_other') {
        showOtherInput.value = true;
      } else {
        showOtherInput.value = false;
        GetPurpose(newStakeholder); 
        Q3(newStakeholder);
      }
    };

    // Info icon on Q3: type of explanation 
    const Q3 = async (selectedStakeholder) => {
      const { chat } = openai();
      try {
        const messages = [
          {
            role: 'system',
            content: 'You are a product manager with experience in managing AI products.',
          },
          {
            role: 'user',
            content: `
            
            Provide a concise suggestion of 15 words max on the type of explanation a data scientist should consider for a model targeted for 
            ${selectedStakeholder.value} would require for the following ML model: ${props.MLTask}, used in the context of ${props.usageContext}. 

        The explanation types options are: 
          - Global explainations: High-level understanding of the model's overall behavior.
          - Local explanations: Insights into specific predictions or decisions.
          - Data Disclosure: Transparency regarding the data used to train or inform the model.
          - Other

        Briefly justify your suggestion by explaining why this explanation type is most relevant or valuable for this specific stakeholder in the given context. 
        You can suggest more than one option.
     
`,
          },
        ];

        const chatResponse = await chat(messages, 'gpt-3.5-turbo');
        Q3_response.value = chatResponse.split('\n\n')[0];
        
      } catch (error) {
        console.error('Error fetching chat response for stakeholders:', error);
      }
    };

    // Example Info icon: language level question. 

    const Q4 = async () => {
  const { chat } = openai();
  try {
    const messages = [
      {
        role: 'system',
        content: 'You are a product manager with experience in managing AI products.',
      },
      {
        role: 'user',
        content: `
          Provide an example of the language level requirement that a data scientist should consider when meeting 
          the explainability expectations for ${selectedStakeholderLabel.value} who has the following purposes for explainability: ${purpose.value} and 
          the type of explanations for a ${props.MLTask} is ${typeofExplanation.value}.
        `,
      },
    ];

    const chatResponse = await chat(messages, 'gpt-3.5-turbo');
    Q4_response.value = chatResponse.split('\n\n')[0];
  } catch (error) {
    console.error('Error fetching chat response for stakeholders:', error);
  }
};



watch([stakeholder, purpose, typeofExplanation], ([newStakeholder, newPurpose, newTypeofExplanation]) => {
  if (newStakeholder && newPurpose.length > 0 && newTypeofExplanation.length > 0) {
    Q4(); 
  }
}, { deep: true });



// example info icon for test plan question:
const Q5 = async () => {
  console.log("Q5 is called");
  const { chat } = openai();
  try {
    const messages = [
      {
        role: 'system',
        content: 'You are a product manager with experience in managing AI products.',
      },
      {
        role: 'user',
        content: `
          Provide an example of a test that a data scientist should consider when meeting 
          the explainability expectations for a person.
        `,
      },
    ];

    const chatResponse = await chat(messages, 'gpt-3.5-turbo');
    console.log("Q5 chatResponse:", chatResponse);
    Q5_response.value = chatResponse.split('\n\n')[0];
    console.log("Q5_response updated:", Q5_response.value);
  } catch (error) {
    console.error('Error fetching chat response for Q5:', error);
  }
};

watch([language_expectations], ([newLanguageExpectations]) => {
  if (newLanguageExpectations.length > 0) {
    Q5();
  }
}, { immediate: true });


    onMounted(() => {
      getChatResponse();
      GetStakeholders();
      //GetPurpose();
      //Q3();
      //Q4();
      Q5();
      
    });

    return {
      response,
      Q3_response,
      Q4_response,
      Q5_response,
      stakeholder,
      stakeholder_list,
      //selectedStakeholderLabel,
      purpose,
      purpose_list,
      showOtherInput,
      typeofExplanation,
      language_expectations,
      test_plan,
      OtherStakeholder,
      dataModalHeaders,
      dataModalRows,
      dataItem,
      addField,
      deleteField,
      onStakeholderChange,
      selectedStakeholderLabel,
      selectedPurposeLabels,
    };
  },
};
</script>


<style scoped>
.AIgeneratedtext {
  background-color: #efe8c7;
}

.info-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: black;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 20px;
  font-weight: bold;
  font-family: Arial, cursive;
  font-size: 10px;
  cursor: pointer;
  margin-left: 5px;
  position: relative;
}

.tooltip {
  display: none;
  position: absolute;
  background-color: rgb(0, 0, 0);
  color: rgb(255, 255, 255);
  border: 1px solid #ccc;
  padding: 10px;
  font-size: 12px;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 200px;
  top: 25px; 
  left: 0;
  z-index: 10;
}

.info-container:hover .tooltip {
  display: block;
}

.info-container {
  position: relative;
  display: inline-block;
}
</style>
