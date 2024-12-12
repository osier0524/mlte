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

<!-- Table-->
          <div v-for="(field, fieldIndex) in dataItem.fields" :key="fieldIndex">
            <h3 class="no-margin-sub-header">
             <b>Stakeholder or Recipient {{ fieldIndex + 1 }} </b> 
             <InfoIcon>
                      Field type, e.g., number, string, Boolean, data, image,
                      audio. 
                      <br/>
                    </InfoIcon>
            </h3>

            <!-- 1) Stakeholders List -->
  <USelect
    placeholder="Select an option..."
    icon="i-heroicons-magnifying-glass-20-solid"
    v-model="stakeholder"
    :options="stakeholder_list"
  />
  <!-- Conditionally show input field for 'Other' -->
  <br />
  <div v-if="showOtherInput">
    <label for="otherInput"><b>*Specify Other Stakeholder</b> </label>
    <UInput v-model="OtherStakeholder" style="width: 300px;" />
    <br />
  </div>

  <!-- 2) Purpose -->
  <label><b>Purpose of the Explanations</b></label>
  <InfoIcon>
                      Field type, e.g., number, string, Boolean, data, image,
                      audio.
                    </InfoIcon>
  <USelect
    placeholder="Select an option..."
    icon="i-heroicons-magnifying-glass-20-solid"
    v-model="purpose"
    :options="purpose_list"
  />

            <div>
              <div class="inline-input-left">
                <UsaTextInput v-model="field.name">
                  <template #label>
                    Field Name
                    <InfoIcon> Field name. </InfoIcon>
                  </template>
                </UsaTextInput>
              </div>

              <div class="inline-input-right">
                <UsaTextInput v-model="field.description">
                  <template #label>
                    Field Description
                    <InfoIcon> Short field description. </InfoIcon>
                  </template>
                </UsaTextInput>
              </div>
            </div>

            <div>
              <div class="inline-input-left">
                <UsaTextInput v-model="field.type">
                  <template #label>
                    Field Type
                    <InfoIcon>
                      Field type, e.g., number, string, Boolean, data, image,
                      audio.
                    </InfoIcon>
                  </template>
                </UsaTextInput>
              </div>

              <div class="inline-input-right">
                <UsaTextInput v-model="field.expected_values">
                  <template #label>
                    Expected Values
                    <InfoIcon>
                      Expected values for field, e.g., any, range, enumeration.
                    </InfoIcon>
                  </template>
                </UsaTextInput>
              </div>
            </div>

            <div>
              <div class="inline-input-left">
                <UsaTextInput v-model="field.missing_values">
                  <template #label>
                    Handling Missing Values
                    <InfoIcon>
                      How to interpret missing values, e.g., null, empty string.
                    </InfoIcon>
                  </template>
                </UsaTextInput>
              </div>

              <div class="inline-input-right">
                <UsaTextInput v-model="field.special_values">
                  <template #label>
                    Handling Special Values
                    <InfoIcon>
                      How to interpret special values, e.g., 999, N/A.
                    </InfoIcon>
                  </template>
                </UsaTextInput>
              </div>
            </div>
            <DeleteButton
              class="margin-button"
              @click="deleteField(dataItemIndex, fieldIndex)"
            >
              Delete Field
            </DeleteButton>
            <hr />
          </div>

          <AddButton class="margin-button" @click="addField(dataItemIndex)">
            Add Stakeholder
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
    const stakeholder = ref('');
    const stakeholder_list = ref([]);
    const purpose = ref([]);
    const purpose_list = ref([]);
    const OtherStakeholder = ref('');
    const showOtherInput = ref(false);

    const handleSelection = () => {
      showOtherInput.value = stakeholder.value === 'stakeholder_other';
    };

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
            content: `Write a concise sentence explaining a potential consequence of neglecting proper explainability in the context of ${props.MLTask} and ${props.usageContext} for a non-technical stakeholder of the product.`,
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

    const GetPurpose = async () => {
      const { chat } = openai();
      try {
        const messages = [
          {
            role: 'system',
            content: 'You are a product manager with experience in managing AI products.',
          },
          {
            role: 'user',
            content: `Generate purposes for explainability in the context of ${props.MLTask} and ${props.usageContext}.`,
          },
        ];

        const chatPurpose = await chat(messages, 'gpt-3.5-turbo');
        const PurposeArray = chatPurpose
          .split('\n')
          .filter(purpose => purpose.trim() !== '')
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

    onMounted(() => {
      getChatResponse();
      GetStakeholders();
      GetPurpose();
    });

    return {
      response,
      stakeholder,
      stakeholder_list,
      purpose,
      purpose_list,
      showOtherInput,
      OtherStakeholder,
      dataModalHeaders,
      dataModalRows,
      dataItem,
      addField,
      deleteField,
    };
  },
};
</script>


<style scoped>
.AIgeneratedtext {
  background-color: #efe8c7;
}
</style>
