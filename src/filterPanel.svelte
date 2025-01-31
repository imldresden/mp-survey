<script>
  import FilterGroup from "./components/filterGroup.svelte";
  import { Accordion, Badge, Heading } from 'flowbite-svelte';

  import Timeline from "./components/timeline.svelte";
  import { filterBy } from "./store"

  export let freq = {};
  export let selectTopics = [];
  export const filteredFreq = {};
  
	export let data;
	export let filteredData;

  $:topics = selectTopics

  const removeSelection = (select) => {
    $filterBy.forEach((prop) => {
      if (prop.values) {
          prop.selected = prop.selected.filter((topic) => topic !== select);
      } else {
        prop.categories.forEach((option) => {
            option.selected = option.selected.filter(
              (topic) => topic !== select
            );
        });
      }
    });
    $filterBy = $filterBy;
  };

  let secondary = true

  const onChange = () => {
    console.log(secondary)
    $filterBy.forEach((prop) => {
      if (secondary && prop.values) {
        prop.valuesTemp = structuredClone(prop.values);
        prop.values = prop.values.filter((c) => c.contains("(-)"));
      } else if (!secondary && prop.values) {
        prop.values = prop.valuesTemp.filter((c) => c);
      }
    });
    $filterBy = $filterBy;
  };

</script>

<div class="accordion-container">
  
  <div>
		{#each topics as topic }
			<Badge class="p-2 h-5 ml-1" large on:close={(e) => removeSelection(topic)}>{topic}</Badge>
		{/each}
  </div>

  
  <Timeline {filteredData} {data} />
  
  <Accordion multiple>
    {#each $filterBy as prop}
      <!-- <Panel square extend style="padding-bottom: 30px; padding-left:10px"> -->

      {#if prop.values && prop.values.length > 0}
          <FilterGroup {...prop} freqGroup={freq[prop.name]} on:message />
      {:else}
        <Heading tag="h6" class="mt-5">{prop.groupName}</Heading>
        {#each prop.categories as option}
            <FilterGroup
              {...option}
              freqGroup={freq[option.name]}
              on:message
            />
        {/each}
      {/if}
    {/each}
  </Accordion>

</div>
