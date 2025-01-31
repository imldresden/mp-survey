<script>
	import Select from 'svelte-select';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	let filterText = '';

	let value = null;

	export let name = '';
	export let items = [];

	function handleFilter(e) {
		if (value?.find((i) => i.label === filterText)) return;
		if (e.detail.length === 0 && filterText.length > 0) {
			const prev = items.filter((i) => !i.created);
			items = [...prev, { value: filterText, label: filterText, created: true }];
		}
	}

	function handleChange(e) {
		items = items.map((i) => {
			delete i.created;
			return i;
		});
		dispatch('message', { prop: value, name: name });
	}

	let color = window.getComputedStyle(document.body).getPropertyValue("background-color");
	let altcolor = document.documentElement.classList.contains("dark") ? "var(--alt-color-dark)" : "var(--alt-color-light)";

</script>

<div class="select">
	<Select 
		on:change={handleChange}
		multiple
		on:filter={handleFilter}
		bind:filterText
		bind:value
		{items}
		--background={color}
		--list-background={color}
		--item-hover-bg={altcolor}
		--multi-item-bg={altcolor}
	>
		<div slot="item" let:item>
			{item.created ? 'Add new: ' : ''}
			{item.label}
		</div>
	</Select>
</div>

<style>
</style>
