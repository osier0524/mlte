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


            <UAccordion multiple :items="leadingQuestions" :ui="{ wrapper: 'flex flex-col w-full' }">
                <!-- <template #default="{ item, index, open }">
                    <div class="flex items-center cursor-pointer">
                        <UIcon
                            name="i-heroicons-chevron-right-20-solid"
                            class="w-5 h-5 me-2 transform transition-transform duration-200"
                            :class="[open && 'rotate-90']"
                        />
                        <label><b>{{ item.label }}</b></label>
                    </div>
                </template> -->

                <template #default="{ item, index, open }">
                    <div class="flex items-center cursor-pointer">
                        <label><b>{{ item.label }}</b></label>
                        <UIcon
                            name="i-heroicons-chevron-right-20-solid"
                            class="w-5 h-5 ms-auto transform transition-transform duration-200"
                            :class="[open && 'rotate-90']"
                        />
                    </div>
                </template>

                <template #real-world-factors>
                    <div class="leading-question">
                        <p style="color: initial; font-size: 1rem;">
                            In real-world scenarios, what kinds of factors might cause the data your model receives to deviate from ideal or expected conditions? 
                            You may want to consider this from three perspectives: Environmental Factors, System-related Factors, and Human Factors.
                            If you don’t know, please consult with the stakeholders for clarification.
                            Please fill in the answers under the "Real-world Factors" column in the table.
                        </p>
                        <br />
                        <p style="color: initial; font-size: 1rem;">
                            Examples for your scenario:
                        </p>
                        <UTable :rows="factors_example" />
                        <div class="input-button-wrapper">
                            <UInput v-model="newFactor" placeholder="Add Real-world Factor" />
                            <UButton color="yellow" :ui="{ rounded: 'rounded-full' }" @click="addFactor">Add To Table</UButton>
                        </div>
                        <br />
                    </div>
                </template>

                <template #perturbations>
                    <div class="leading-question">
                        <p style="color: initial; font-size: 1rem;">
                            How might these factors impact the input data that your model receives?
                            Please fill in the answers under the "Perturbations" column in the table.
                        </p>
                        <UTable :rows="pert_example" />
                    </div>
                </template>

                <template #output>
                    <div class="leading-question">
                        <p style="color: initial; font-size: 1rem;">
                            How would these changes in input data affect your model’s predictions? Would they lead to incorrect predictions, decreased accuracy, or unstable outputs?
                            Perturbations are domain-specific, so please be as detailed as possible. If you're unsure about the specifics, consult with the stakeholders for clarification.
                            Please fill in the answers under the "Effects on Outputs" column in the table.
                        </p>
                    </div>
                </template>

                <template #robustness>
                    <div class="leading-question">
                        <p style="color: initial; font-size: 1rem;">
                            When your input data is affected by these real-world factors, do you expect your model’s predictions to remain consistent?
                            Please fill in the answers under the "Need Robustness?" column in the table. (Y/N)
                        </p>
                    </div>
                </template>

                <template #tolerance>
                    <div class="leading-question">
                        <p style="color: initial; font-size: 1rem;">
                            To what extent do you want your model to tolerate these changes in input without affecting predictions?
                            <br />
                            Please define three tolerance levels for your model based on how much it can tolerate changes in input without significantly affecting predictions. 
                            You can categorize these levels as Low, Moderate, and High. 
                            After defining the tolerance levels, please select which one applies to this specific requirement.
                            Please fill in the answers under the "Tolerance Level" column in the table.
                        </p>
                    </div>
                </template>
            </UAccordion>

            <!-- <div v-if="robustnessTaskType ==='Image Processing'">
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
            </div> -->

            <!-- <div v-if="robustnessTaskType ==='NLP'">
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
            </div> -->

            <div>
                <UTable :rows="tableData" :columns="columns" >
                    <!-- <template #body-cell="{ item, column, rowIndex}"> -->
                    <template #factor-data="{ row, column }">
                        <UInput v-model="row.factor" placeholder="Add Real-world Factor"/>
                    </template>
                    <template #pert-data="{ row, column }">
                        <UInput v-model="row.pert" placeholder="Add Perturbation"/>
                    </template>

                    <template #output-data="{ row, column }">
                        <UInput v-model="row.output" placeholder="Add Effects on Outputs"/>
                    </template>

                    <template #robust-data="{ row, column }">
                        <UInput v-model="row.robust" placeholder="Y/N"/>
                    </template>

                    <template #tolerance-data="{ row, column }">
                        <UInput v-model="row.tolerance" placeholder="Add Tolerance Level"/>
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

            const leadingQuestions = [{
                label: 'Real-world Factors',
                defaultOpen: true,
                slot: 'real-world-factors',
            }, {
                label: 'Potential Effects on Model Inputs(Perturbations)',
                defaultOpen: false,
                slot: 'perturbations',
            }, {
                label: 'Potential Effects on Model Outputs',
                defaultOpen: false,
                slot: 'output',
            }, {
                label: 'Need Robustness?',
                defaultOpen: false,
                slot: 'robustness',
            }, {
                label: 'Tolerance Level',
                defaultOpen: false,
                slot: 'tolerance',
            }]

            const items = [{
                label: 'Getting Started',
                icon: 'i-heroicons-information-circle',
                defaultOpen: true,
                content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed neque elit, tristique placerat feugiat ac, facilisis vitae arcu. Proin eget egestas augue. Praesent ut sem nec arcu pellentesque aliquet. Duis dapibus diam vel metus tempus vulputate.'
            }]

            // Define variables related to the table
            const columns = ref([
                { key: 'factor', label: 'Real-world Factors' },
                { key: 'pert', label: 'Perturbations' },
                { key: 'output', label: 'Effects on Outputs' },
                { key: 'robust', label: 'Need Robustness?' },
                { key: 'tolerance', label: 'Tolerance Level' },
            ]);

            const tableData = ref([
                { factor: '', pert: '', output: '', robust: '', tolerance: '' },
            ]);

            // const people = [{
            //     id: 1,
            //     name: 'Lindsay Walton',
            //     title: 'Front-end Developer',
            //     email: 'lindsay.walton@example.com',
            //     role: 'Member'
            //     }, {
            //     id: 2,
            //     name: 'Courtney Henry',
            //     title: 'Designer',
            //     email: 'courtney.henry@example.com',
            //     role: 'Admin'
            //     },
            // ];


            const factors_example = [
                { 
                    Environmental: 'Weather Conditions(rain, fog, snow)',
                    System: 'Camera shake',
                    Human: 'Stickers, paint on signs',
                },
                { 
                    Environmental: 'Lighting Conditions(difference between day and night, high brightness)',
                    System: 'Camera broken',
                    Human: 'Adversarial attacks',
                },
                {
                    Environmental: 'Background Complexity',
                    System: 'Lens dirt',
                },
                { 
                    Environmental: 'Sign Damage'
                },
            ];

            const pert_example = [
                {
                    Factor: 'Rain',
                    Perturbation: 'Raindrops on the camera lens can create blurriness or obstructions in certain areas of the image.',
                },
                {
                    Factor: 'Low Light at Night',
                    Perturbation: 'Critical features of the traffic signs (e.g., text, shapes) may be lost or harder to discern.'
                },
                {
                    Factor: 'Camera Shake',
                    Perturbation: 'Traffic signs might appear skewed or stretched in images due to the camera\'s angle of approach or distance.'
                }
            ]

            const newFactor = ref('');

            const addFactor = () => {
                if (!newFactor.value.trim()) {
                    return;
                }
                // If only one row in the table, and it's empty, replace it with the new factor
                if (tableData.value.length === 1 && Object.values(tableData.value[0]).every((val) => !val)) {
                    tableData.value[0].factor = newFactor.value;
                    newFactor.value = '';
                    return;
                }

                const exists = tableData.value.some((row) => row.factor === newFactor.value);
                if (!exists) {
                    tableData.value.push({
                        factor: newFactor.value,
                        pert: '',
                        output: '',
                        robust: '',
                        tolerance: '',
                    });
                    newFactor.value = '';
                }
            };

            const addRow = () => {
                tableData.value.push({
                    factor: '',
                    pert: '',
                    output: '',
                    robust: '',
                    tolerance: '',
                });
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
                leadingQuestions,
                items,
                columns,
                tableData,
                factors_example,
                pert_example,
                newFactor,
                addFactor,
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

.input-button-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.leading-question p {
    color: inherit;
}

.default-paragraph {
    color: initial;
    font-size: 1rem;
}

</style>