<script>
  import { onMount } from "svelte";
  import { afterUpdate, createEventDispatcher } from 'svelte';
  import { AccordionItem, Button, P } from "flowbite-svelte";
	import { CheckOutline } from "flowbite-svelte-icons";

	import { filterBy } from "../store"
  
  export let name;
  export let selected;
  export let values;
  export let freqGroup;

  const dispatch = createEventDispatcher();

  let listVal = [];
  const sShowCount = 10;
  let showCount = 10;

  const updateShowCount = (newCount) => {
    const temp = values.sort((a, b) => {
      return freqGroup[b] - freqGroup[a];
    });
    if (newCount > 0) {
      showCount = newCount;
    } else {
      showCount = sShowCount;
    }
    const data = values.slice(0, showCount);
    listVal = data.map((name) => {
      return name;
    });
  };


  onMount(async () => {
    updateShowCount(showCount);
  });
</script>

<AccordionItem>
  <P weight="semibold" slot="header">
    {name}
    {#if selected !== undefined && selected.length}
      <span style="color:gray">
        ({selected.length})
      </span>
    {/if}
  </P>
  <div class="space-y-1 flex-col flex flex-shrink items-start">
    {#each listVal as value}
      <Button
        color="none"
        size="xs"
        on:click={() => {
          const f = $filterBy;
          f.forEach((filter) => {
            if ("groupName" in filter) {
              filter.categories.forEach((cate) => {
                if (cate.values.includes(value)) {
                  if (!cate.selected.includes(value)) {
                    cate.selected.push(value);
                  } else {
                    cate.selected = cate.selected.filter(i => i !== value);
                  }
                    
                  return;
                }
              });
            } else {
              if (filter.values.includes(value)) {
                if (!filter.selected.includes(value)) {
                  filter.selected.push(value);
                } else {
                  filter.selected = filter.selected.filter(i => i !== value)
                }
                return;
              }
            }
          });

          if(!selected.includes(value)){
          	selected.push(value);
					} else {
						selected = selected.filter(i => i !== value)
					}

          filterBy.update(_ => f);
        }}>
				{#if selected.includes(value)}
				<CheckOutline class="w-3 h-3 mr-1"/>
				{/if}
				{"(" + freqGroup[value] + ") " + value}
				</Button
      >
    {/each}
  </div>

  <div class="space-y-1" style="padding-top: 3px">
    {#if showCount > sShowCount}
      <Button
        outline
        class="border-0"
        size="xs"
        on:click={() => updateShowCount(showCount - 10)}>
        see less
      </Button>
    {/if}
    {#if showCount < values.length}
      <Button
        outline
        class="border-0"
        size="xs"
        on:click={() => updateShowCount(showCount + 10)}
      >
        see more
      </Button>
    {/if}
  </div>
</AccordionItem>

<style>
</style>
