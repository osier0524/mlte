<template>
    <div>
        <br />
            <!-- API call -->
            <div class="chatgptcall">
                <p><b>What's Evolution?</b> </p>
                <p>
                </p>
            </div>
            <br />
            <!-- <p> <b>What does that mean for your project?</b></p> -->
            <p><b>Create a Quality Scenario</b></p>
            <br/>

            <label><b>For All Evolutions</b></label>
            <br />

            <label><b>Evolution Frequency</b></label>
            <p>
                How often should this model be evolved? Should it be on a fixed schedule (e.g., monthly or quarterly) or triggered by specific events? 
                If you prefer a fixed schedule, go to the interval section. 
                If you prefer specific triggers, go to the triggers section.
            </p>
            <br />

            <label><b>Evolution Interval</b></label>
            <p> What is the evolution interval of your model? (Unit: days)</p>
            <UInput placeholder="e.g., 30" v-model="evolutionInterval" />
            <br />

            <label><b>Evolution Triggers</b></label>
            <br />
            <label>Emergency Case</label>
            <p>Are there particular conditions that require immediate model evolution (e.g., significant performance drop)? 
                Please define metrics and thresholds for these critical conditions.
            </p>
            <UInput placeholder="e.g., Significant performance drop" v-model="emergencyCase" />
            <br />
            <label>Regular Case</label>
            <p>If using dynamic triggers, which specific indicators (e.g., data drift, concept drift) will be monitored to initiate evolution?
                Please define metrics and thresholds for routine monitoring and gradual evolution triggers.
            </p>
            <UInput placeholder="e.g., Data drift, concept drift" v-model="regularCase" />
            <br />

            <p>Examples for your scenario</p>
            <UTable :rows="triggers_example" />

            <label><b>Deployment</b></label>
            <br />
            <label><b>Deployment Strategies</b></label>
            <p>
                What deployment strategy will be used to introduce new model versions?
            </p>
            <USelect
                placeholder="Select Deployment Strategies..."
                :options="['In-place', 'Blue/green', 'Canary', 'Linear', 'All-at-once']"
                icon="i-heroicons-magnifying-glass-20-solid"
                v-model="deploymentStrategy"
            />
            <br />
            <label><b>Downtime Tolerance</b></label>
            <p>
                What is the maximum downtime tolerance for deployment? (Units: ms)
            </p>

            <label><b>Versioning and Rollback</b></label>
            <br />
            <label><b>Restore Time</b></label>
            <p>
                What is the maximum acceptable time to restore the previous model? (Units: mins)
            </p>
            <UInput placeholder="e.g., 10" v-model="restoreTime" />
            <br />
            <label><b>Downtime Tolerance</b></label>
            <p>
                What is the maximum downtime tolerance for rollback? (Units: ms)
            </p>    
            <UInput placeholder="e.g., 100" v-model="rollbackDowntime" />
            <br/>
            <label><b>Version Retention</b></label>
            <p>
                How many previous model versions should be stored to ensure a reliable rollback option?
            </p>
            <UInput placeholder="e.g., 3" v-model="versionRetention" />
            <br />
            <br />

            <label><b>Retrain Latency</b></label>
            <p>
                What is the maximum acceptable retrain duration? (Units: mins)
            </p>
            <UInput placeholder="e.g., 120" v-model="retrainLatency" />

        <br/>
    </div>

    <div>

    </div>
</template>

<script lang="ts">

    export default {
        name: 'EvolutionForm',
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
                { key: 'factor', label: 'Real-world Factors' },
                { key: 'pert', label: 'Perturbations' },
                { key: 'output', label: 'Effects on Outputs' },
                { key: 'robust', label: 'Need Robustness?' },
                { key: 'tolerance', label: 'Tolerance Level' },
            ]);

            const tableData = ref([
                { factor: '', pert: '', output: '', robust: '', tolerance: '' },
            ]);


            const triggers_example = [
                {
                    Case: 'Emergency',
                    Trigger: "Accuracy",
                    Evalution_Method: "Classification Accuracy",
                    Trigger_Value: "< 75%",
                },
                {
                    Case: 'Emergency',
                    Trigger: "Latency",
                    Evalution_Method: "Inference Latency",
                    Trigger_Value: "> 500ms",
                },
                {
                    Case: 'Regular',
                    Trigger: "Data Drift",
                    Evalution_Method: 'KL Divergence',
                    Trigger_Value: "> 0.1",
                },
                {
                    Case: 'Regular',
                    Trigger: "Concept Drift",
                    Evalution_Method: 'Label Distribution Shift',
                    Trigger_Value: "> 10%",
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
                columns,
                tableData,
                triggers_example,
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

.input-grid {
  display: grid;
  flex-direction: column;
  gap: 1rem;
}

.input-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}


</style>