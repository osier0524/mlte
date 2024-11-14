<template>
  <div>
      <br />
          <!-- API call -->
          <div class="chatgptcall">
          <p><b>What's Robustness?</b> </p>
          <p>
              Robustness in machine learning is a model's ability to make consistent predictions even when its input data undergoes slight changes. A robust model should deliver stable outputs, maintaining accuracy and reliability under minor variations in data.
               
              <br/>
              
              <span class="AIgeneratedtext">{{ robustnessDefinition }} </span>
              <span class="AIgeneratedtext">{{ response }} </span>
          </p>
          </div>
          <br />
          <!-- <p> <b>What does that mean for your project?</b></p> -->
          <p><b>Create a Quality Scenario</b></p>
          <br/>

          <!-- Task Type Selection -->
          <label><b>Task Type</b></label>
          <div class="info-container">
              <span class="info-icon">i</span>
              <div class="tooltip">What task type type is yours?</div>
          </div>
          <USelect
              placeholder="Select Task Type..."
              :options="['Image Processing', 'NLP', 'Structured Data','Others']"
              icon="i-heroicons-magnifying-glass-20-solid"
              v-model="robustnessTaskType"
          />
          <br />


          <label><b>Real-world Perturbation</b></label>
          <div class="info-container">
              <span class="info-icon">i</span>
              <div class="tooltip">In real-world scenarios, what types of perturbations might affect the input data your model receives?</div>
          </div>
          <UInput 
              v-model="perturbations" 
              placeholder="e.g., lighting conditions, background noise, sensor errors" />
          <br />

          <label><b>Most Critical Perturbation</b></label>
          <div class="info-container">
              <span class="info-icon">i</span>
              <div class="tooltip">From the perturbations you mentioned, which type of variation are you most concerned about?</div>
          </div>
          <UInput 
              v-model="perturbations" 
              placeholder="Bluriness"  />
          <br />

          <div v-if="robustnessTaskType ==='Image Processing'">
              <label><b>Transformation Option (Image Perocessing)</b></label>
              <div class="info-container">
                  <span class="info-icon">i</span>
                  <div class="tooltip">To test your model's robustness, choose a transformation that you want to apply to your test data.</div>
              </div>
              <USelect
                  placeholder="Select an option..."
                  :options="['Occulusion', 'Rotation', 'Blurring','Brightness Adjustment', 'Scaling', 'Noise Injection']"
                  icon="i-heroicons-magnifying-glass-20-solid"
                  v-model="transformation"
              />
              <br />
          </div>

          <div v-if="robustnessTaskType ==='NLP'">
              <label><b>Transformation Option (NLP)</b></label>
              <div class="info-container">
                  <span class="info-icon">i</span>
                  <div class="tooltip">To test your model's robustness, choose a transformation that you want to apply to your test data.</div>
              </div>
              <USelect
                  placeholder="Select an option..."
                  :options="['Synonym Replacement', 'Typos', 'Word Removal','Word Order Shuffling', 'Punctuation Change', 'Entity Replacement', 'Text Augmentation']"
                  icon="i-heroicons-magnifying-glass-20-solid"
                  v-model="transformation"
              />
              <br />
          </div>

          <!-- <UTable :rows="people" /> -->

          <div>
              <UTable :rows="tableData" :columns="columns" >
                  <!-- <template #body-cell="{ item, column, rowIndex}"> -->
                  <template #pert-data="{ row, column }">
                      <UInput v-model="row.name" placeholder="Add Perturbation"/>
                  </template>

                  <template #tolerance-data="{ row, column }">
                      <UInput v-model="row.email" placeholder="Add Tolerance Level"/>
                  </template>
              </UTable>
          </div>

          <div>
              <UButton color="yellow" :ui="{ rounded: 'rounded-full' }" @click="addRow">+</UButton>
              <UButton color="yellow" :ui="{ rounded: 'rounded-full' }" @click="removeRow" :disabled="tableData.length === 0">-</UButton>
          </div>

      <br/>
  </div>

  <div>

  </div>
</template>

<script lang="ts">

  export default {
      name: 'RobustnessForm',
      props: {
          problemType: {
              required: true,
          },
          MLTask: {
              required: true,
          },
          usageContext: {
              required: true,
          },
      },
      setup(props) {

          // Define variables related to the table
          const columns = ref([
              { key: 'pert', label: 'Perturbations' },
              { key: 'tolerance', label: 'Tolerance Level' },
          ]);

          const tableData = ref([
              { pert: '', tolerance: '' },
          ]);

          const addRow = () => {
              tableData.value.push({ pert: '', tolerance: '' });
          };

          const removeRow = () => {
              if (tableData.value.length > 0) {
                  tableData.value.pop();
              }
          };

          const robustnessTaskType = ref('');
          const response = ref('');
          const robustnessDefinition = ref<string | null>(null);

          const chat_role = 'You are a specialized data scientist with knowledge in both software engineering and data science.';

          
          const basicDefinition = `Robustness in machine learning is a model's ability to make consistent predictions even when its input data undergoes slight changes. A robust model should deliver stable outputs, maintaining accuracy and reliability under minor variations in data.`;
          
          const generateRobustnessDefinition = async () => {
              const { chat } = openai();
              try {
                  const messages = [
                      {
                          role: 'system',
                          content: chat_role,
                      },
                      {
                          role: 'user',
                          content: `For the following query, craft a response that defines robustness in the user's specific context in a single sentence. 
                          The response should: 
                          - Describe robustness using user's scenario:
                              Problem Type: ${props.problemType}
                              ML Task: ${props.MLTask}
                              Usage Context: ${props.usageContext}
                          - Avoid general definitions like "slight changes in input data" or "consistent predictions." 
                          Instead, directly use a concrete example to illustrate what robustness means in this scenario.
                          - Start with "In your context,"
                          Example: "In your context, robustness means that if measurements are taken under slightly varied lighting conditions 
                          affecting the perceived size or color of features, the model should still accurately classify the iris species." 
                          Ensure the response is only one sentence and directly defines robustness with a practical example, as shown in the example above.`,
                      },
                  ];

                  const chatResponse = await chat(messages);
                  robustnessDefinition.value = chatResponse;
              } catch (error) {
                  console.error('Error generating definition: ', error);
              }
          };

          watch(
              [() => props.problemType, () => props.MLTask, () => props.usageContext],
              ([problemType, MLTask, usageContext]) => {
                  if (problemType && MLTask && usageContext) {
                      generateRobustnessDefinition();
                  }
              },
              { immediate: true }
          );

          return {
              columns,
              tableData,
              addRow,
              removeRow,
              robustnessTaskType,
              response,
              robustnessDefinition,
          };
      },
  }
</script>

<style scoped>
.AIgeneratedtext{
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

#cautiontext{
font-size: 12px;
font-style: italic;
text-align: center;
}

</style>