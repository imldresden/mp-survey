<script>
  import { Pane, Splitpanes } from "svelte-splitpanes";
  import { P, Button, Drawer, Heading } from "flowbite-svelte";
  import { CloseSolid, ReplyOutline } from "flowbite-svelte-icons";
  import PaperCard from "./components/paperCard.svelte";
  import FilterPanel from "./filterPanel.svelte";
  import Header from "./header.svelte";
  import Vis from "./vis.svelte";
  import structure from "./data/survey-config.json";
  import dataMeta from "./data/survey-data.json";
  import { searchFilter, timeFilters, filterBy } from "./store";
  import { sineIn } from "svelte/easing";
  import SearchField from "./components/searchField.svelte";

  let transitionParams = {
    x: -320,
    duration: 200,
    easing: sineIn,
  };

  let headerPx = 45;
  let backdrop = false;
  let activateClickOutside = true;
  let drawerHidden = false;
  let innerHeight = 0;
  let showVis = true;
  let showPapers = true;
  let filteredData = [];
  let meta = {};
  let freq = {};
  let filteredFreq = {};
  let selectTopics = [];

  //Restructuring parts of the data passed in
  dataMeta.meta.forEach((prop) => {
    meta[prop.name] = prop;
  });

  $filterBy = structure.filterBy;
  $filterBy.forEach((prop) => {
    if (prop.values) {
      if (prop.name in meta && meta[prop.name].type === "MultiSelect") {
        prop.selected = [];
      }
    } else {
      prop.categories.forEach((option) => {
        if (option.name in meta && meta[option.name].type === "MultiSelect") {
          option.selected = [];
        }
      });
    }
  });
  addMissingValues();

  function freqCount(prop, arrValue, freqDict) {
    if (prop in meta && meta[prop].type === "MultiSelect") {
      if (arrValue.length == 1 && arrValue[0] === "") {
        return;
      }
      arrValue.forEach((value) => {
        if (prop in freq) {
          freqDict[prop][value]
            ? freqDict[prop][value]++
            : (freqDict[prop][value] = 1);
        } else {
          freqDict[prop] = {};
          freqDict[prop][value] = 1;
        }
      });
    }
  }

  dataMeta.data.forEach((paper) => {
    Object.entries(paper).forEach(([prop, arrValue]) => {
      freqCount(prop, arrValue, freq);
    });
    paper["selected"] = false;
  });

  function addMissingValues() {
    $filterBy.forEach((group) => {
      if ("groupName" in group) {
        group["categories"].forEach((cate) => {
          if (!("values" in cate)) {
            const topics = new Set();
            dataMeta.data.forEach((paper) => {
              if (cate["name"] in paper) {
                paper[cate["name"]].forEach((word) => {
                  topics.add(word);
                });
              }
            });
            cate["values"] = [...topics];
          }
        });
      } else {
        if (!("values" in group)) {
          const topics = new Set();
          dataMeta.data.forEach((paper) => {
            if (group["name"] in paper) {
              paper[group["name"]].forEach((word) => {
                topics.add(word);
              });
            }
          });
          group["values"] = [...topics];
        }
      }
    });
  }

  function applyFilters(searchFilter, timeFilters, filterBy) {
    //This is a shallow copy, we only interested in the order
    let startingPoint = [...dataMeta.data];

    //Filter by search bar
    if (searchFilter !== "" && searchFilter.length > 2) {
      startingPoint = startingPoint.filter((paper) =>
        paper.Name.toLowerCase().includes(searchFilter.toLowerCase())
      );
    }
    if (timeFilters.start > 0)
      startingPoint = startingPoint.filter(
        (paper) =>
          timeFilters.start <= +paper.Year && +paper.Year <= timeFilters.end
      );

    const re = new RegExp("([0-9]+)");

    //Filter by categories
    filterBy.forEach((group) => {
      if (group.values) {
        if (group.selected && group.selected.length > 0) {
          const selected = group.selected.map((sel) => {
            return re.test(sel) ? sel.split(") ")[1] : sel;
          });
          let res = [];
          startingPoint.forEach((paper) => {
            let found = false;
            if (Array.isArray(paper[group.name])) {
              const listCate = paper[group.name];
              found = true;
              selected.forEach((prop) => {
                if (listCate.includes(prop) === false) {
                  found = false;
                  return;
                }
              });
            } else if (typeof paper[group.name] === "string") {
              found = selected.includes(paper[group.name]);
            }

            if (found) {
              res.push(paper);
            }
          });
          startingPoint = res;
        }
      } else {
        group.categories.forEach((option) => {
          if (option.selected && option.selected.length > 0) {
            const selected = option.selected.map((sel) => {
              return re.test(sel) ? sel.split(") ")[1] : sel;
            });
            let res = [];
            startingPoint.forEach((paper) => {
              let found = false;
              if (Array.isArray(paper[option.name])) {
                const listCate = paper[option.name];
                found = true;
                selected.forEach((prop) => {
                  if (listCate.includes(prop) === false) {
                    found = false;
                    return;
                  }
                });
              } else if (typeof paper[option.name] === "string") {
                found = selected.includes(paper[option.name]);
              }
              if (found) {
                res.push(paper);
              }
            });
            startingPoint = res;
          }
        });
      }
    });
    Object.entries(startingPoint).forEach(([prop, arrValue]) => {
      freqCount(prop, arrValue, filteredFreq);
    });
    filteredData = startingPoint.sort((p1, p2) => {
      if (Number(p1.Year) < Number(p2.Year)) {
        return 1;
      } else {
        return -1;
      }
    });
    selectTopics = [];
    filterBy.forEach((filter) => {
      if ("groupName" in filter) {
        filter.categories.forEach((cate) => {
          selectTopics = selectTopics.concat(cate.selected);
        });
      } else {
        selectTopics = selectTopics.concat(filter.selected);
      }
    });
    filterBy = [...filterBy];
  }

  function toggleView() {
    if (showVis) {
      showVis = false;
      showPapers = true;
    } else {
      showVis = true;
      showPapers = false;
    }
  }

  let breakPoint = 1024;
  let width;
  $: if (width >= breakPoint) {
    drawerHidden = false;
    activateClickOutside = false;
    showVis = true;
    showPapers = true;
  } else {
    drawerHidden = true;
    activateClickOutside = true;
    showVis = false;
    showPapers = true;
  }

  $: applyFilters($searchFilter, $timeFilters, $filterBy);

  const clearSelections = () => {
    $filterBy.forEach((prop) => {
      if (prop.values) {
        prop.selected = [];
      } else {
        prop.categories.forEach((option) => {
          option.selected = [];
        });
      }
    });
    $filterBy = $filterBy;
  };
</script>

<svelte:head>
    <title>{structure.topView.title}</title> 
</svelte:head>
<svelte:window bind:innerHeight bind:innerWidth={width} />

<Header
  detailView={structure.detailView.show}
  topView={structure.topView}
  {freq}
  closeFn={() => (drawerHidden = !drawerHidden)}
  toggleParams={ {
    hidden: width >= breakPoint,
    func: toggleView,
    vis: showVis,
    papers: showPapers
  }}
  showTitle={!drawerHidden}
  {headerPx}
/>

<Drawer
  transitionType="fly"
  {backdrop}
  {transitionParams}
  bind:hidden={drawerHidden}
  bind:activateClickOutside
  id="sidebar"
>
  <div class="flex">
    <Heading tag="h5">{structure.topView.title}</Heading>
    <Button
      pill={true}
      outline
      class="!p-1 border-0"
      size="xs"
      on:click={() => (drawerHidden = !drawerHidden)}
    >
      <CloseSolid class="w-4 h-4" />
    </Button>
  </div>
  <hr style="margin:15px" />

  <div class="fliter-papers">
    <Heading tag="h6">Filters:</Heading>
    <Button
      pill={true}
      outline
      class="!p-1 border-0"
      size="xs"
      on:click={clearSelections}
    >
      <ReplyOutline class="w-5 h-5" />
    </Button>
  </div>

  <div class="m-5">
    <SearchField />
  </div>
  
  <FilterPanel
    {freq}
    {selectTopics}
    {filteredData}
    data={dataMeta.data}
  />
</Drawer>

<main class="mx-auto">
  <!--  -->
  <Splitpanes 
    style="height:{innerHeight - headerPx}px;width:{innerWidth +
      (width <= breakPoint || drawerHidden
        ? 2
        : transitionParams.x + 2)}px;float: right;position:initial;"
  >
    {#if showVis}
      <Pane size={showPapers ? 70 : 100}>
        <Vis data={filteredData} />
      </Pane>
    {/if}

    {#if showPapers}
      <Pane>
        <div class="num-papers dark:bg-gray-900">
          <P>Number of papers: {filteredData.length}/{dataMeta.data.length}</P>
        </div>

        <div class="card-container dark:bg-gray-900">
          {#each filteredData as paper, i}
            <PaperCard
              index={i}
              {paper}
              {structure}
              {meta}
            />
          {/each}
        </div>
      </Pane>
    {/if}
  </Splitpanes>
</main>

<style>
  .card-container {
    height: calc(100% - 44px);
    overflow: auto;
  }
  .num-papers {
    padding: 10px 10px;
    display: flex;
    justify-content: space-between;
  }
  .fliter-papers {
    padding: 0px 0px 0px 0px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
