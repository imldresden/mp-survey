<script>
	import { Input, CloseButton } from 'flowbite-svelte'
	import { SearchOutline } from 'flowbite-svelte-icons'
	import { searchFilter } from '../store';


	function clearSearch() {
		$searchFilter = '';
	}
</script>

<div class="solo-container solo-container-prop">
	<Input bind:value={$searchFilter}  placeholder="Search">
		<SearchOutline slot="left"/>
		<CloseButton slot="right" on:click={clearSearch} />
	</Input>
</div>


<style>
	.solo-container {
		margin-right:5px;
		margin-left:5px;
		width: 100% 
	}

	.solo-container-prop {
		display: flex;
		justify-content: center;
		align-items: center;
	}

</style>
