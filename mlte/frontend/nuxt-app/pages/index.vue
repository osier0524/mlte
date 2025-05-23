<template>
  <NuxtLayout name="base-layout">
    <UsaBreadcrumb :items="path" />
    <div style="display: flex">
      <div class="split-div">
        <b>Model</b>
        <UsaSelect
          :options="modelOptions"
          :model-value="selectedModel"
          @update:modelValue="selectModel($event, false)"
        />
        <br />
      </div>

      <div class="split-div">
        <b>Version</b>
        <UsaSelect
          :options="versionOptions"
          :model-value="selectedVersion"
          @update:modelValue="selectVersion($event)"
        />
        <br />
      </div>

      <div>
        <!-- Placeholder for when the search functionality is implemented
        <label class="usa-label" style="margin-top: 0px;">Search</label>
        <UsaTextInput v-model="searchInput" style="width: 100%;"/> -->
      </div>
    </div>

    <UsaAccordion multiselectable bordered>
      <UsaAccordionItem label="Negotiation Cards">
        <div class="scrollable-table-div">
          <p>
            A negotiation card is a document with a series of discussion points
            to be documented during a negotiation between all project
            stakeholders at the project's outset. It is then used as a reference
            throughout development and is updated at prescribed negotiation
            points.
          </p>
          <table class="table usa-table usa-table--borderless">
            <thead>
              <tr>
                <th data-sortable scope="col" role="columnheader">ID</th>
                <th data-sortable scope="col" role="columnheader">Timestamp</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="card in negotiationCards" :key="card.id">
                <th scope="row">{{ card.id }}</th>
                <td>{{ card.timestamp }}</td>
                <td>
                  <NuxtLink
                    :to="{
                      path: 'negotiation-card',
                      query: {
                        model: card.model,
                        version: card.version,
                        artifactId: card.id,
                      },
                    }"
                  >
                    <UsaButton class="primary-button"> Edit </UsaButton>
                  </NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
          <NuxtLink
            :to="{
              path: 'negotiation-card',
              query: {
                model: selectedModel,
                version: selectedVersion,
              },
            }"
          >
            <UsaButton
              :disabled="selectedModel === '' || selectedVersion === ''"
              class="primary-button"
              style="float: left"
            >
              New
            </UsaButton>
          </NuxtLink>
          <p
            v-if="selectedModel === '' || selectedVersion === ''"
            style="float: left; color: red"
          >
            Select a model and version to start a new negotiation card here.
          </p>
        </div>
      </UsaAccordionItem>

      <UsaAccordionItem label="Reports">
        <div class="scrollable-table-div">
          <p>
            A report is a human and machine-readable summary of all knowledge
            gained about a model during the MLTE process.
          </p>
          <table class="table usa-table usa-table--borderless">
            <thead>
              <tr>
                <th data-sortable scope="col" role="columnheader">ID</th>
                <th data-sortable scope="col" role="columnheader">Timestamp</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in reports" :key="report.id">
                <th scope="row">{{ report.id }}</th>
                <td>{{ report.timestamp }}</td>
                <td>
                  <NuxtLink
                    :to="{
                      path: 'report',
                      query: {
                        model: report.model,
                        version: report.version,
                        artifactId: report.id,
                      },
                    }"
                  >
                    <UsaButton class="primary-button"> Edit </UsaButton>
                  </NuxtLink>
                  <NuxtLink
                    :to="{
                      path: 'export-report',
                      query: {
                        model: report.model,
                        version: report.version,
                        artifactId: report.id,
                      },
                    }"
                  >
                    <UsaButton class="primary-button"> Export </UsaButton>
                  </NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
          <NuxtLink
            :to="{
              path: 'report',
              query: {
                model: selectedModel,
                version: selectedVersion,
              },
            }"
          >
            <UsaButton
              :disabled="selectedModel === '' || selectedVersion === ''"
              class="primary-button"
              style="float: left"
            >
              New
            </UsaButton>
          </NuxtLink>
          <p
            v-if="selectedModel === '' || selectedVersion === ''"
            style="float: left; color: red"
          >
            Select a model and version to start a new report.
          </p>
        </div>
      </UsaAccordionItem>

      <UsaAccordionItem label="Specifications">
        <div class="scrollable-table-div">
          <p>
            A specification (spec) defines the model requirements that must be
            satisfied to ensure successful integration with the target system.
          </p>
          <UsaTable
            :headers="cardSpecReportHeaders"
            :rows="specifications"
            borderless
            class="table"
          />
        </div>
      </UsaAccordionItem>

      <UsaAccordionItem label="Validated Specification">
        <div class="scrollable-table-div">
          <p>
            Validated Specification are produced by combining a specification
            with its corresponding results; this artifact communicates how well
            a model performed against all of its requirements.
          </p>
          <UsaTable
            :headers="validatedSpecHeaders"
            :rows="validatedSpecs"
            borderless
            class="table"
          />
        </div>
      </UsaAccordionItem>

      <!-- <UsaAccordionItem label="Results">
        <div class="scrollable-table-div">
          <p>
            Results encode whether or not the values generated during evidence
            collection pass their corresponding validation threshold. They are
            produced by feeding values through the relevant condition callbacks
            provided in the MLTE specification.
          </p>
          <UsaTable :headers="resultsHeaders" borderless class="table" />
        </div>
      </UsaAccordionItem> -->

      <UsaAccordionItem label="Values">
        <div class="scrollable-table-div">
          <p>
            Values are the atomic unit of model evaluation in MLTE. A value is
            any artifact produced by a MLTE measurement for the purposes of
            model evaluation.
          </p>
          <UsaTable
            :headers="valuesHeaders"
            :rows="values"
            borderless
            class="table"
          />
        </div>
      </UsaAccordionItem>

      <UsaAccordionItem label="Critiques">
        <div class="scrollable-table-div">
          <p>
            Critiques are the result of the quality inspection process. They
            provide a detailed evaluation of the model's performance and
            adherence to the specified requirements.
          </p>
          <table class="table usa-table usa-table--borderless">
              <thead>
                <tr>
                  <th data-sortable scope="col" role="columnheader">ID</th>
                  <th scope="col" role="columnheader" style="text-align: right; padding-right: 2.5rem;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <template
                  v-for="(artifact, i) in artifactsInDatabase" :key="artifact.artifact_id"
                >
                  <tr v-if="findMatchingCard(artifact.name)" >
                    <th scope="row">{{ artifact.name }}</th>
                    <td style="text-align: right; padding-right: 0.5rem;">
                      <NuxtLink
                        
                        :to="{
                          path: 'critiques',
                          query: {
                            model: negotiationCards[i].model,
                            version: negotiationCards[i].version,
                            artifactId: negotiationCards[i].id,
                            intId: artifact.artifact_id,
                          },
                        }"
                      >
                        <UsaButton class="primary-button"> Critiques </UsaButton>
                      </NuxtLink>
                    </td>
                  </tr>
                </template>
              </tbody>
          </table>
        </div>
      </UsaAccordionItem>

    </UsaAccordion>
  </NuxtLayout>
</template>

<script setup lang="ts">
import axios from 'axios';

const config = useRuntimeConfig();
const token = useCookie("token");
const path = ref([
  {
    href: "/",
    text: "",
  },
]);

// fetch artifact data from the server
interface Artifact {
  artifact_id: number;
  name: string;
  project_description: string;
  ml_task?: string;
  usage_context?: string;
  target_audience?: string;
  dataset_description?: string;
}

const artifactsInDatabase = ref<Artifact[]>([])

function findMatchingCard(artifactName: String) {
  return negotiationCards.value.find(card => card.id === artifactName);
}

onMounted(async() => {
  try {
    const response = await axios.get(
      config.public.apiPath + "/artifacts"
    )
    artifactsInDatabase.value = response.data
  } catch (error) {
    console.error("Error fetching artifacts:", error)
  }
})

const modelOptions = ref<{ value: string; text: string }[]>([]);
const versionOptions = ref<{ value: string; text: string }[]>([]);
const { data: modelList } = await useFetch<string[]>(
  config.public.apiPath + "/model",
  {
    method: "GET",
    headers: {
      Authorization: "Bearer " + token.value,
    },
  },
);
if (modelList.value) {
  modelList.value.forEach((modelName: string) => {
    modelOptions.value.push({ value: modelName, text: modelName });
  });
}

const selectedModel = useCookie("selectedModel");
selectedModel.value = selectedModel.value || "";
const selectedVersion = useCookie("selectedVersion");
selectedVersion.value = selectedVersion.value || "";

const cardSpecReportHeaders = ref([
  { id: "id", label: "ID", sortable: true },
  { id: "timestamp", label: "Timestamp", sortable: true },
]);

const validatedSpecHeaders = ref([
  { id: "id", label: "ID", sortable: true },
  { id: "specid", label: "SpecID", sortable: true },
  { id: "timestamp", label: "Timestamp", sortable: true },
]);

const valuesHeaders = ref([
  { id: "id", label: "ID", sortable: true },
  { id: "measurement", label: "Measurement", sortable: true },
  { id: "type", label: "Type", sortable: true },
  { id: "timestamp", label: "Timestamp", sortable: true },
]);

const negotiationCards = ref<
  { id: string; timestamp: string; model: string; version: string }[]
>([]);
const specifications = ref<
  { id: string; timestamp: string; model: string; version: string }[]
>([]);
const reports = ref<
  { id: string; timestamp: string; model: string; version: string }[]
>([]);
const validatedSpecs = ref<
  {
    id: string;
    specid: string;
    timestamp: string;
    model: string;
    version: string;
  }[]
>([]);
const values = ref<
  {
    id: string;
    measurement: string;
    type: string;
    timestamp: string;
    model: string;
    version: string;
  }[]
>([]);

if (modelOptions.value !== null && modelOptions.value.length > 0) {
  const modelList = modelOptions.value.map((model) => {
    return model.value;
  });
  if (!modelList.includes(selectedModel.value)) {
    selectedModel.value = "";
    selectedVersion.value = "";
  }
  if (selectedModel.value !== "") {
    console.log("Selected model: ", selectedModel.value);
    await selectModel(selectedModel.value, true);
    const versionList = versionOptions.value.map((version) => {
      return version.value;
    });
    if (!versionList.includes(selectedVersion.value)) {
      selectedVersion.value = "";
    }
    if (selectedVersion.value !== "") {
      await selectVersion(selectedVersion.value);
    }
  }
}

// Update the selected model for the artifact store.
async function selectModel(modelName: string, initialPageLoad: boolean) {
  try {
    console.log("Selected model: ", selectedModel.value);
    if (!initialPageLoad) {
      selectedVersion.value = "";
    }
    if (modelName === "") {
      versionOptions.value = [];
      clearArtifacts();
      return;
    }

    await $fetch(config.public.apiPath + "/model/" + modelName + "/version", {
      retry: 0,
      method: "GET",
      headers: {
        Authorization: "Bearer " + token.value,
      },
      onRequestError() {
        requestErrorAlert();
      },
      onResponse({ response }) {
        if (response._data) {
          selectedModel.value = modelName;
          versionOptions.value = [];
          response._data.forEach((version: string) => {
            versionOptions.value.push({
              value: version,
              text: version,
            });
          });
        }
      },
      onResponseError() {
        responseErrorAlert();
      },
    });

    versionOptions.value.sort(function (
      a: { value: string; text: string },
      b: { value: string; text: string },
    ) {
      if (a.value < b.value) {
        return -1;
      } else if (a.value > b.value) {
        return 1;
      } else {
        return 0;
      }
    });

  } catch (error) {
    console.error("Error selecting model:", error);
  }
}

// Update the selected version for the artifact store.
async function selectVersion(versionName: string) {
  selectedVersion.value = versionName;
  if (versionName === "") {
    clearArtifacts();
    return;
  }

  await $fetch(
    config.public.apiPath +
      "/model/" +
      selectedModel.value +
      "/version/" +
      versionName +
      "/artifact",
    {
      retry: 0,
      method: "GET",
      headers: {
        Authorization: "Bearer " + token.value,
      },
      onRequestError() {
        requestErrorAlert();
      },
      onResponse({ response }) {
        if (response._data) {
          selectedVersion.value = versionName;
          populateArtifacts(
            selectedModel.value,
            selectedVersion.value,
            response._data,
          );
        }
      },
      onResponseError() {
        responseErrorAlert();
      },
    },
  );
}

// Populate artifacts for a given model and version.
// TODO : Do better typing on the artifactList and artifact
function populateArtifacts(model: string, version: string, artifactList: any) {
  try {
    console.log("Processing artifacts:", model, version);
    console.log("Artifact list sample:", artifactList[0]);

    artifactList.forEach((artifact: any) => {
      try {

        artifact.header.timestamp = new Date(
          artifact.header.timestamp * 1000,
        ).toLocaleString("en-US");
        // Negotiation card
        if (artifact.header.type === "negotiation_card") {
          if (isValidNegotiation(artifact)) {
            console.log("Model: ", model);
            console.log("Version: ", version);
            negotiationCards.value.push({
              id: artifact.header.identifier,
              timestamp: artifact.header.timestamp,
              model,
              version,
            });
            console.log("negotiationCards: ", negotiationCards.value);
          }
        }
        // Report
        else if (artifact.header.type === "report") {
          if (isValidReport(artifact)) {
            reports.value.push({
              id: artifact.header.identifier,
              timestamp: artifact.header.timestamp,
              model,
              version,
            });
          }
        }
        // Spec
        else if (artifact.header.type === "spec") {
          if (isValidSpec(artifact)) {
            specifications.value.push({
              id: artifact.header.identifier,
              timestamp: artifact.header.timestamp,
              model,
              version,
            });
          }
        }
        // Validated spec
        else if (artifact.header.type === "validated_spec") {
          if (isValidValidatedSpec(artifact)) {
            validatedSpecs.value.push({
              id: artifact.header.identifier,
              specid: artifact.body.spec_identifier,
              timestamp: artifact.header.timestamp,
              model,
              version,
            });
          }
        }
        // Value
        if (artifact.header.type === "value") {
          if (isValidValue(artifact)) {
            values.value.push({
              id: artifact.header.identifier.slice(0, -6),
              measurement: artifact.body.metadata.measurement_type,
              type: artifact.body.value.value_type,
              timestamp: artifact.header.timestamp,
              model,
              version,
            });
          }
        }
      } catch (error) {
        console.error("Error processing artifact:", artifact.header?.identifier, error);
      }
    });
  } catch (error) {
    console.error("Error populating artifacts:", error);
  }
}

// Clear all artifacts from local state.
function clearArtifacts() {
  negotiationCards.value = [];
  reports.value = [];
  specifications.value = [];
  validatedSpecs.value = [];
  values.value = [];
}

// When negotiationCards changes, print all values in negotiationCards
watch(negotiationCards, (newCards) => {
  for (const card of newCards) {
    console.log("Negotiation card: ", card);
  }
}, { deep: true });
</script>

<style>
.scrollable-table-div {
  overflow-y: auto;
  height: 18em;
}

.table {
  width: 100%;
}

.split-div {
  width: 34ch;
  margin-right: 1em;
}

.scrollable-div {
  border: 1px solid gray;
  overflow-y: auto;
  height: 11em;
  padding-left: 0.4em;
}
</style>
