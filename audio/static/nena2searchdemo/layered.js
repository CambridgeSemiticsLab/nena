/*eslint-env jquery*/

/* global configData */
/* global corpusData */

/* --- OVERVIEW ----------------------------------------------
 *
 * This is a Web App that implements Layered Search on a Corpus
 *
 * See: https://annotation.github.io/text-fabric/tf/about/layeredsearch.html
 *
 * The app is meant to work in with a static HTML file, not served by a webserver,
 * not even localhost, although both should be possible.
 *
 * The code consists of 10 classes, divided into 3 chapters.
 *
 * The 10 classes define all a service provider.
 * They will each be instantiated by single object.
 *
 * We list them in the order that they are defined in the code.
 *
 * Functional Chapter
 * ==================
 * business logic: getting the corpus data and searching in it
 *
 * Config
 * -----------
 *
 * Manages incoming config data of the corpus
 *
 * Corpus
 * -----------
 *
 * Manages incoming bulk data of the corpus
 *
 * Search
 * -----------
 *
 * Implements the search algorithm
 *
 *
 * Application Chapter
 * ==================
 * generic logic of a typical webapp
 *
 * State
 * -----------
 *
 * The single source of truth about the results of
 * - computations
 * - user interactions
 *
 * Job
 * -----------
 *
 * Breaking up the process in jobs, that can be saved and loaded, im- and exported
 *
 * Gui
 * -----------
 *
 * The Graphical user interface, HTML generation, activating buttons,
 * applying the State to the interface
 *
 * Systems Chapter
 * ==================
 *
 * Low level technical provisions. Logging, Disk access, Local Storage.
 *
 * Disk
 * -----------
 *
 * Uploading and donwloading of files
 *
 * Mem
 * -----------
 *
 * Storing data as key-value pairs in Local Storage
 *
 * Log
 * -----------
 *
 * Messages, to the interface and to the console
 *
 *
 * Main chapter
 * ==================
 *
 * App
 * -----------
 *
 * Orchestrates all of the above classess
 *
 * Takes care that the bulk data can be loaded asynchronously.
 *
 * Main program
 *
 * The trigger that loads everything
 *
 */

/* --- DEFINITIONS CHAPTER ----------------------------------------------
 */

const DEBUG = true

const BOOL = "boolean"
const NUMBER = "number"
const STRING = "string"
const OBJECT = "object"

const QUWINDOW = 10
const MAXINPUT = 1000

const DEFAULTJOB = "search"

const BUTTON = {
  nodeseq: { on: "nodes start at 1", off: "nodes as in TF" },
  autoexec: { on: "auto search", off: "press to search" },
  exec: { no: " ", on: "⚫️", off: "🔴" },
  visible: { on: "🔵", off: "⚪️" },
  expand: {
    on: "- active layers",
    off: "+ all layers",
    no: "no layers",
  },
}

const UNITTEXT = { r: "row unit", a: "context", d: "content" }

const FLAGSDEFAULT = { i: true, m: true, s: false }

const SEARCH = {
  dirty: "fetch results",
  exe: "fetching ...",
  done: "up to date",
}
const TIP = {
  nodeseq: `node numbers start at 1 for each node types
OR
node numbers are exactly as in Text Fabric`,
  autoexec: `search automatically after each change
OR
only search after you hit the search button`,
  expand: "whether to show inactive layers",
  unit: "make this the row unit",
  exec: "whether this pattern is used in the search",
  visible: "whether this layer is visible in the results",
  visibletp: "whether node numbers are visible in the results",
  flagm: `multiline: ^ and $ match:
ON: around newlines
OFF: at start and end of whole text`,
  flags: `single string: . matches all characters:
ON: including newlines
OFF: excluding newlines"`,
  flagi: `ignore
ON: case-insensitive
OFF: case-sensitive"`,
}

/* --- FUNCTIONAL CHAPTER ----------------------------------------------
 */

/* THE DATA
 *
 * The fixed data is in the global vars corpusData and configData.
 *
 * Both kinds of data will be wrapped into Provider objects: Config and Corpus
 * after which the global vars should not be accessed, even for reading.
 * We cannot really enforce this, though.
 *
 * Config is for the small configuration data.
 *
 * Corpus contains the big textual and positional data.
 */

class ConfigProvider {
/* CONFIG
 *
 * Readonly data: defaults, settings, descriptions.
 */

  init() {
    /* try to encapsulate all access to the data inside this class
     */

    const {
      name, description, levels, captions,
      containerType, simpleBase,
      ntypes, ntypesinit, ntypessize,
      utypeOf, dtypeOf,
      layers, visible,
    } = configData

    /* the name of the app
     */
    this.name = name

    /* the description of the configData
     */
    this.description = description

    /* per node type the description of that level
     */
    this.levels = levels

    /* Captions for several elements
     * - title
     */
    this.captions = captions

    /* the base type of the configData, e.g. word or letter
     */
    this.simpleBase = simpleBase

    /* info about layers:
     * per node type and then per layer:
     * - valueMap: mapping from acros to full values: => legend (optional)
     * - pos: the name of the key where the positions for this layer can be found
     *   in the corpusData (some layers share positions for efficiency)
     * - pattern: an example pattern (only used in debug mode)
     * - description: a description of the layer
     */
    this.layers = layers

    /* visibility of layers, per node type and then per layer
     */
    this.visible = visible

    /* ordered list of types in the data, from lowest to highest
     */
    this.ntypes = ntypes

    /* where each node types start: the first TF node number of that type
     */
    this.ntypesinit = ntypesinit

    /* the amount of nodes in each node type
     */
    this.ntypessize = ntypessize

    /* map from type to one-higher type
     */
    this.utypeOf = utypeOf

    /* map from type to one-lower type
     */
    this.dtypeOf = dtypeOf

    /* computed attributes for convenience
     */

    /* the default container type
     * if it is missing, we fill in a middle type
     */
    const pos = Math.round(ntypes.length / 2)
    this.containerType = containerType || ntypes[pos]

    /* array of types in reversed order
     */
    this.ntypesR = [...ntypes]
    this.ntypesR.reverse()

    /* map of types to their index in the array
     */
    const ntypesI = new Map()
    for (let i = 0; i < ntypes.length; i++) {
      ntypesI.set(ntypes[i], i)
    }
    this.ntypesI = ntypesI
  }
}

class CorpusProvider {
/* THE CORPUS
 *
 * Readonly data: texts, positions, the parent relation "up".
 */

  deps({ Log }) {
    this.Log = Log
  }

  init() {
    /* try to encapsulate all access to the data inside this class
     */

    const { texts, positions } = corpusData

    /* full text for a layer
     * - per type and then per layer
    */
    this.texts = texts

    /* mapping from charcter positions to nodes for a layer
     * - per type and then per layer
     */
    this.positions = positions

    this.warmUpData()

    /* Now we have more data in this object:
     *
     * - up: mapping from a node to its parent one level higher
     * - down: mapping from a node to its children one level higher
     * - iPositions: mapping from nodes to character positions for a layer
     *   - per type and then per layer
     */
  }

  warmUpData() {
    /* Expand parts of the data that have been optimized before shipping
     */
    const { Log } = this

    Log.progress(`Decompress up-relation and infer down-relation`)
    this.decompress()
    Log.progress(`Infer inverted position maps`)
    this.invertPositionMaps()
    Log.progress(`Done`)
  }

  decompress() {
    /* The map "up" is expanded. We also compute its converse, "down".
     */
    const { up } = corpusData

    const newUp = new Map()
    const down = new Map()

    for (const line of up) {
      const [spec, uStr] = line.split("\t")
      const u = uStr >> 0
      if (!down.has(u)) {
        down.set(u, new Set())
      }

      const ns = []
      const ranges = spec.split(",")

      for (const range of ranges) {
        const bounds = range.split("-").map(x => x >> 0)
        if (bounds.length == 1) {
          ns.push(bounds[0])
        } else {
          for (let i = bounds[0]; i <= bounds[1]; i++) {
            ns.push(i)
          }
        }
      }
      const downs = down.get(u)
      for (const n of ns) {
        newUp.set(n, u)
        downs.add(n)
      }
    }
    this.up = newUp
    this.down = down
  }

  invertPositionMaps() {
    /* The corpusData contains position-to-node mappings
     * for all relevant nodes.
     * We make the inverses of these mappings here.
     */
    const { positions } = this

    const iPositions = {}

    for (const [nType, tpInfo] of Object.entries(positions)) {
      for (const [layer, pos] of Object.entries(tpInfo)) {
        const iPos = new Map()
        for (let i = 0; i < pos.length; i++) {
          const node = pos[i]
          if (node == null) {
            continue
          }
          if (!iPos.has(node)) {
            iPos.set(node, [])
          }
          iPos.get(node).push(i)
        }
        if (iPositions[nType] == null) {
          iPositions[nType] = {}
        }
        iPositions[nType][layer] = iPos
      }
    }

    this.iPositions = iPositions
  }
}

class SearchProvider {
/* SEARCH EXECUTION
 *
 * The implementation of layered search:
 *
 * 1. gather:
 *    - match the regular expressions against the texts of the layers,
 *    - for each node type, take the intersection of the resulting
 *      nodesets in the layers
 * 2. weed (the heart of the layered search algorithm):
 *    - intersect across node types (using projection to
 *      upward and downward levels
 * 3. compose:
 *    - organize the result nodes around the nodes in a container type
 * 4. display:
 *    - draw the table of results on the interface
 *    - by screenfuls
 *    - make navigation controls for moving the focus through the table
 */

  deps({ Log, Disk, State, Gui, Config, Corpus }) {
    this.Log = Log
    this.Disk = Disk
    this.State = State
    this.Gui = Gui
    this.Config = Config
    this.Corpus = Corpus
  }

  async runQuery() {
    /* Performs a complete query
     * The individual sub steps each check whether there is something to do
     */

    /* LONG RUNNING FUNCTIONS
     *
     * We apply a device to make behaviour more conspicuous on the interface.
     *
     * There are two problems
     *
     * 1. some actions go so fast, that the user does not see them happening
     * 2. some actions take a lot of time, without the user knowing that he must wait
     *
     * To solve that, we apply some CSS transitions to background and border colors.
     * In order to trigger them, we wrap some functions into this sequence:
     *
     * a. add the CSS class "waiting" to some elements
     * b. run the function in question
     * c. remove the CSS class "waiting" from thiose elements.
     *
     * However, when we implement this straightforwardly and synchronously,
     * we do not see any effect, because the browser does not take the trouble
     * to re-render during this sequence.
     *
     * So we need an asynchronous wrapper, and here is what happens:
     *
     * a. add the CSS class "waiting"
     * b. sleep for a fraction of a second
     * c. - now the browser renders the interface and you see the effect of "waiting"
     * d. run the function in question
     * e. remove the CSS class "waiting"
     * f. - when the sequence is done, the browser renders again, and you see the
     *       effect of "waiting" gone
     */

    const { Log, Gui } = this

    const output = $(`#resultsbody,#resultshead`)
    const go = $("#go")
    const expr = $("#exportr")

    Log.progress(`executing query`)
    go.html(SEARCH.exe)
    go.removeClass("dirty")
    go.addClass("waiting")
    output.addClass("waiting")
    /* sleep a number of milliseconds to trigger a rendering of the browser
     */
    await new Promise(r => setTimeout(r, 50))

    this.gather()
    const stats = this.weed()
    Gui.placeStatResults(stats)
    this.composeResults(false)
    this.displayResults()

    go.html(SEARCH.done)
    expr.addClass("active")
    output.removeClass("waiting")
    go.removeClass("waiting")
    $(".dirty").removeClass("dirty")
    Log.progress(`done query`)
  }

  doSearch(nType, layer, lrInfo, regex) {
    /* perform regular expression search for a single layer
     * return character positions and nodes that hold those positions
     */
    const { Corpus: { texts: { [nType]: { [layer]: text } }, positions } } = this
    const { pos: posKey } = lrInfo
    const { [nType]: { [posKey]: pos } } = positions
    const searchResults = text.matchAll(regex)
    const posFromNode = new Map()
    const nodeSet = new Set()
    for (const match of searchResults) {
      const hit = match[0]
      const start = match.index
      const end = start + hit.length
      for (let i = start; i < end; i++) {
        const node = pos[i]
        if (node != null) {
          if (!posFromNode.has(node)) {
            posFromNode.set(node, new Set())
          }
          posFromNode.get(node).add(i)
          nodeSet.add(node)
        }
      }
    }
    return { posFromNode, nodeSet }
  }

  gather() {
    /* perform regular expression search for all layers
     * return for each node type
     *     the intersection of the nodesets found for each layer
     *     for each layer, a mapping of nodes to matched positions
     */
    const { Log, Config: { ntypesR, layers }, State } = this

    const { query } = State.getj()

    State.sets({ resultsComposed: [], resultTypeMap: new Map() })
    const { tpResults } = State.sets({ tpResults: {} })

    for (const nType of ntypesR) {
      const { [nType]: tpInfo = {} } = layers
      const { [nType]: tpQuery } = query
      let intersection = null
      const matchesByLayer = {}

      for (const [layer, lrInfo] of Object.entries(tpInfo)) {
        const box = $(`[kind="pattern"][ntype="${nType}"][layer="${layer}"]`)
        const ebox = $(`[kind="error"][ntype="${nType}"][layer="${layer}"]`)
        Log.clearError(box, ebox)
        const { [layer]: { pattern, flags, exec } } = tpQuery
        if (!exec || pattern.length == 0) {
          continue
        }
        if (pattern.length > MAXINPUT) {
          Log.placeError(
            box,
            ebox,
            `pattern must be less than ${MAXINPUT} characters long`
          )
          continue
        }
        const flagString = Object.entries(flags)
          .filter(x => x[1]).map(x => x[0]).join("")
        let regex
        try {
          regex = new RegExp(pattern, `g${flagString}`)
        } catch (error) {
          Log.placeError(box, ebox, `"${pattern}": ${error}`)
          continue
        }
        const { posFromNode, nodeSet } = this.doSearch(nType, layer, lrInfo, regex)
        matchesByLayer[layer] = posFromNode
        if (intersection == null) {
          intersection = nodeSet
        } else {
          for (const node of intersection) {
            if (!nodeSet.has(node)) {
              intersection.delete(node)
            }
          }
        }
      }
      const matches = matchesByLayer || null
      tpResults[nType] = { matches, nodes: intersection }
    }
  }

  weed() {
    /* combine the search results across node types
     * the current search results will be weeded in place:
     *   the nodesets found per node type will be projected onto other types
     *   and then the intersection with those projected sets will be taken.
     *   This leads to the situation where for each node type there is a nodeset
     *   that maps 1-1 to the nodeset of any other type module projection.
     *  returns statistics: how many nodes there are for each type.
     */
    const { Config: { ntypes }, Corpus: { up, down }, State } = this
    const { tpResults } = State.gets()
    const stats = {}

    /* determine highest and lowest types in which a search has been performed
     */
    let hi = null
    let lo = null

    for (let i = 0; i < ntypes.length; i++) {
      const nType = ntypes[i]
      const { [nType]: { nodes } } = tpResults

      if (nodes != null) {
        if (lo == null) {
          lo = i
        }
        hi = i
      }
    }

    /* we are done if no search has been performed
     */
    if (hi == null) {
      return stats
    }

    /*
     * Suppose we have types 0 .. 7 with hi and lo as follows.
     *
     *  0
     *  1
     *  2=hi
     *  3
     *  4
     *  5=lo
     *  6
     *  7
     *
     *  Then we walk through the layers as follows
     *
     *  2 dn 3 dn 4 dn 5
     *  5 up 4 up 3 up 2 up 1 up 0
     *  5 dn 6 dn 7
     */

    /* intersect downwards
     */

    for (let i = hi; i > lo; i--) {
      const upType = ntypes[i]
      const dnType = ntypes[i - 1]
      const { [upType]: { nodes: upNodes }, [dnType]: resultsDn = {} } = tpResults
      let { nodes: dnNodes } = resultsDn
      const dnFree = dnNodes == null

      /* project upnodes downward if there was no search in the down type
       */
      if (dnFree) {
        dnNodes = new Set()
        for (const un of upNodes) {
          if (down.has(un)) {
            for (const dn of down.get(un)) {
              dnNodes.add(dn)
            }
          }
        }
        resultsDn["nodes"] = dnNodes
      }

      /* if there was a search in the down type, weed out the down nodes that
       * have no upward partner in the up nodes
       */
      for (const dn of dnNodes) {
        if (!up.has(dn) || !upNodes.has(up.get(dn))) {
          dnNodes.delete(dn)
        }
      }
    }

    /* intersect upwards (all the way to the top)
     */
    for (let i = lo; i < ntypes.length - 1; i++) {
      const dnType = ntypes[i]
      const upType = ntypes[i + 1]
      const { [upType]: resultsUp = {}, [dnType]: { nodes: dnNodes } } = tpResults

      const upNodes = new Set()
      for (const dn of dnNodes) {
        if (up.has(dn)) {
          upNodes.add(up.get(dn))
        }
      }
      resultsUp["nodes"] = upNodes
    }

    /* project downwards from the lowest level to the bottom type
     */
    for (let i = lo; i > 0; i--) {
      const upType = ntypes[i]
      const dnType = ntypes[i - 1]
      const { [upType]: { nodes: upNodes }, [dnType]: resultsDn = {} } = tpResults
      const dnNodes = new Set()
      for (const un of upNodes) {
        if (down.has(un)) {
          for (const dn of down.get(un)) {
            dnNodes.add(dn)
          }
        }
      }
      resultsDn["nodes"] = dnNodes
    }

    /* collect statistics
     */
    for (const [nType, { nodes }] of Object.entries(tpResults)) {
      stats[nType] = nodes.size
    }
    return stats
  }

  composeResults(recomputeFocus) {
    /* divided search results into chunks by containerType
     * The results are organized by the nodes that have containerType as node type.
     * Each result will have three parts:
     *   ancestor nodes: result nodes of higher types that contain the container node
     *   container node: one node of the containerType
     *   descendant nodes: all descendants of the container node
     * The result at the position that has currently focus on the interface,
     * is marked by means of a class
     *
     * recomputeFocus = true:
     * If we do a new compose because the user has changed the container type
     * we estimate the focus position in the new container type based on the
     * focus position in the old container type
     * We adjust the interface to the new focus pos (slider and number controls)
     */
    const { Config: { ntypesI, utypeOf }, Corpus: { up }, State } = this
    const { tpResults, resultsComposed: oldResultsComposed } = State.gets()

    if (tpResults == null) {
      State.sets({ resultsComposed: null })
      return
    }

    const {
      focusPos: oldFocusPos,
      prevFocusPos: oldPrevFocusPos,
      dirty: oldDirty,
      containerType,
    } = State.getj()

    const { [containerType]: { nodes: containerNodes } = {} } = tpResults

    const oldNResults = oldResultsComposed == null ? 1 : oldResultsComposed.length
    const oldNResultsP = Math.max(oldNResults, 1)
    const oldRelative = oldFocusPos / oldNResultsP
    const oldPrevRelative = oldPrevFocusPos / oldNResultsP

    const {
      resultsComposed, resultTypeMap,
    } = State.sets({ resultsComposed: [], resultTypeMap: new Map() })

    if (containerNodes) {
      for (const cn of containerNodes) {

        /* collect the upnodes
         */
        resultTypeMap.set(cn, containerType)

        let un = cn
        let uType = containerType

        const ancestors = []

        while (up.has(un)) {
          un = up.get(un)
          uType = utypeOf[uType]
          resultTypeMap.set(un, uType)
          ancestors.unshift(un)
        }

        /* collect the down nodes
         */
        const descendants = this.getDescendants(cn, ntypesI.get(containerType))

        resultsComposed.push({ cn, ancestors, descendants })
      }
    }
    const nResults = resultsComposed == null ? 0 : resultsComposed.length
    let focusPos = oldDirty ? -2 : oldFocusPos,
      prevFocusPos = oldDirty ? -2 : oldPrevFocusPos
    if (recomputeFocus) {
      focusPos = Math.min(nResults, Math.round(nResults * oldRelative))
      prevFocusPos = Math.min(nResults, Math.round(nResults * oldPrevRelative))
    } else {
      if (focusPos == -2) {
        focusPos = nResults == 0 ? -1 : 0
        prevFocusPos = -2
      } else if (focusPos > nResults) {
        focusPos = 0
        prevFocusPos = -2
      }
    }

    State.setj({ focusPos, prevFocusPos })
  }

  getDescendants(u, uTypeIndex) {
    /* get all descendents of a node, organized by node type
     * This is an auxiliary function for composeResults()
     * The function calls itself recursively for all the children of
     * the node in a lower level
     * returns an array of subarrays, where each subarray corresponds to a child node
     * and has the form [node, [...descendants of node]]
     */
    if (uTypeIndex == 0) {
      return []
    }

    const { Config: { dtypeOf, ntypes }, Corpus: { down }, State } = this
    const { resultTypeMap } = State.gets()

    const uType = ntypes[uTypeIndex]
    const dType = dtypeOf[uType]
    const dTypeIndex = uTypeIndex - 1

    const dest = []

    for (const d of down.get(u)) {
      resultTypeMap.set(d, dType)
      if (dTypeIndex == 0) {
        dest.push(d)
      } else {
        dest.push([d, this.getDescendants(d, dTypeIndex, resultTypeMap)])
      }
    }
    return dest
  }

  getHLText(iPositions, matches, text, valueMap) {
    /* get highlighted text for a node
     * The results of matching a pattern against a text are highlighted within that text
     * returns a sequence of spans, where a span is an array of postions plus a boolean
     * that indicated whether the span is highlighted or not.
     * Used by display() and tabular() below
     */
    const hasMap = valueMap != null

    const spans = []
    let str = ""
    let curHl = null

    for (const i of iPositions) {
      const ch = text[i]
      if (hasMap) {
        str += ch
      }
      const hl = matches.has(i)
      if (curHl == null || curHl != hl) {
        const newSpan = [hl, ch]
        spans.push(newSpan)
        curHl = hl
      } else {
        spans[spans.length - 1][1] += ch
      }
    }
    const tip = hasMap ? valueMap[str] : null
    return { spans, tip }
  }

  getLayers(nType, layers, visibleLayers, includeNodes) {
    const { [nType]: definedLayers = {} } = layers
    const { [nType]: tpVisible } = visibleLayers
    const nodeLayer = includeNodes ? ["_"] : []
    return nodeLayer.concat(Object.keys(definedLayers)).filter(x => tpVisible[x])
  }

  displayResults() {
    /* Displays composed results on the interface.
     * Results are displayed in a table, around a focus position
     * We only display a limited amount of results around the focus position,
     * but the user can move the focus position in various ways.
     * Per result this is visible:
     *   Ancestor nodes are rendered highlighted
     *   The container nodes themselves are rendered as single nodes
     *     if they have content, otherwise they are left out
     *   The descendants of the container node are rendered with
     *   all of descendants (recursively),
     *     where the descendants that have results are highlighted.
     */
    const {
      Config: { simpleBase, layers, ntypesI, ntypesinit },
      Corpus: { texts, iPositions },
      State,
      Gui,
    } = this

    const { resultTypeMap, tpResults, resultsComposed } = State.gets()
    const {
      settings: { nodeseq },
      visibleLayers, focusPos, prevFocusPos,
    } = State.getj()

    if (tpResults == null) {
      State.sets({ resultsComposed: null })
      return
    }

    const genValueHtml = (nType, layer, node) => {
      /* generates the html for a layer of node, including the result highlighting
       */
      if (layer == "_") {
        const num = nodeseq ? node - ntypesinit[nType] + 1 : node
        return `<span class="n">${num}</span>`
      }
      const { [nType]: { [layer]: { pos: posKey, valueMap } } } = layers
      const { [nType]: { [layer]: text } } = texts
      const { [nType]: { [posKey]: iPos } } = iPositions
      const nodeIPositions = iPos.get(node)
      const { [nType]: { matches: { [layer]: matches } = {} } } = tpResults
      const nodeMatches =
        matches == null || !matches.has(node) ? new Set() : matches.get(node)

      const { spans, tip } = this.getHLText(nodeIPositions, nodeMatches, text, valueMap)
      const hasTip = tip != null
      const tipRep = (hasTip) ? ` title="${tip}"` : ""

      const html = []
      const multiple = spans.length > 1 || hasTip
      if (multiple) {
        html.push(`<span${tipRep}>`)
      }
      for (const [hl, val] of spans) {
        const hlRep = hl ? ` class="hl"` : ""
        html.push(`<span${hlRep}>${val}</span>`)
      }
      if (multiple) {
        html.push(`</span>`)
      }
      return html.join("")
    }

    const genNodeHtml = node => {
      /* generates the html for a node, including all layers and highlighting
       */
      const [n, children] = typeof node === NUMBER ? [node, []] : node
      const nType = resultTypeMap.get(n)
      const { [nType]: { nodes } = {} } = tpResults
      const tpLayers = this.getLayers(nType, layers, visibleLayers, true)
      const nLayers = tpLayers.length
      const hasLayers = nLayers > 0
      const hasSingleLayer = nLayers == 1
      const hasChildren = children.length > 0
      if (!hasLayers && !hasChildren) {
        return ""
      }

      const hlClass =
        simpleBase && ntypesI.get(nType) == 0 ? "" : nodes.has(n) ? " hlh" : "o"

      const hlRep = hlClass == "" ? "" : ` class="${hlClass}"`
      const lrRep = hasSingleLayer ? "" : ` m`
      const hdRep = hasChildren ? "h" : ""

      const html = []
      html.push(`<span${hlRep}>`)

      if (hasLayers) {
        html.push(`<span class="${hdRep}${lrRep}">`)
        for (const layer of tpLayers) {
          html.push(`${genValueHtml(nType, layer, n)}`)
        }
        html.push(`</span>`)
      }

      if (hasChildren) {
        html.push(`<span>`)
        for (const ch of children) {
          html.push(genNodeHtml(ch))
        }
        html.push(`</span>`)
      }

      html.push(`</span>`)

      return html.join("")
    }

    const genAncestorsHtml = ancestors => {
      /* generates the html for the ancestor nodes of a result
       */
      const html = ancestors.map(anc => genNodeHtml(anc))
      return html.join(" ")
    }

    const genResHtml = (cn, descendants) => {
      /* generates the html for the container node and descendant nodes of a result
       */
      const html = []
      html.push(`${genNodeHtml(cn)} `)
      for (const desc of descendants) {
        html.push(genNodeHtml(desc))
      }
      return html.join("")
    }

    const genResultHtml = (i, result) => {
      /* generates the html for a single result
       */
      const isFocus = i == focusPos
      const isPrevFocus = i == prevFocusPos
      const { ancestors, cn, descendants } = result
      const ancRep = genAncestorsHtml(ancestors)
      const resRep = genResHtml(cn, descendants)
      const focusCls = isFocus
        ? ` class="focus"`
        : isPrevFocus
        ? ` class="pfocus"`
        : ""

      return `
  <tr${focusCls}>
    <th>${i + 1}</th>
    <td>${ancRep}</td>
    <td>${resRep}</td>
  </tr>
    `
    }

    const genResultsHtml = () => {
      /* generates the html for all relevant results around a focus position in the
       * table of results
       */
      if (resultsComposed == null) {
        return ""
      }
      const startPos = Math.max((focusPos || 0) - 2 * QUWINDOW, 0)
      const endPos = Math.min(
        startPos + 4 * QUWINDOW + 1,
        resultsComposed.length - 1
      )
      const html = []
      for (let i = startPos; i <= endPos; i++) {
        html.push(genResultHtml(i, resultsComposed[i], i == focusPos))
      }
      return html.join("")
    }

    const html = genResultsHtml()
    const resultsbody = $("#resultsbody")
    resultsbody.html(html)
    Gui.applyFocus()
  }

  /* RESULTS EXPORT
   * Exports the current results to a tsv file
   * All result nodes will be exported in a table
   * with one node per row:
   * the first column is the node number, the second one is the node type
   * and the layers are the remaining columns
   *
   * N.B. So we do not export composed results, but raw result nodes.
   *
   * The resulting tsv is written in UTF-16-LE encoding for optimal interoperability
   * with Excel
   */
  tabular() {
    const {
      Config: { layers, ntypes, ntypesinit },
      Corpus: { texts, iPositions }, State,
    } = this

    const { settings: { nodeseq } } = State.getj()

    const { tpResults } = State.gets()
    if (tpResults == null) {
      return null
    }
    const { visibleLayers } = State.getj()

    const headFields = ["type"]
    const nodeFields = new Map()

    for (let i = 0; i < ntypes.length; i++) {
      const nType = ntypes[i]
      const { [nType]: { matches, nodes } } = tpResults

      if (nodes == null) {
        continue
      }

      const { [nType]: tpLayerInfo } = layers
      const { [nType]: tpTexts } = texts
      const { [nType]: tpIPositions } = iPositions

      const exportLayers = this.getLayers(nType, layers, visibleLayers, false)
      for (const node of nodes) {
        if (!nodeFields.has(node)) {
          nodeFields.set(node, new Map())
        }
        const fields = nodeFields.get(node)
        fields.set("type", nType)
      }
      for (const layer of exportLayers) {
        const tpLayer = `${nType}-${layer}`
        headFields.push(tpLayer)

        const { [layer]: { pos: posKey, valueMap } } = tpLayerInfo
        const { [layer]: text } = tpTexts
        const { [posKey]: iPos } = tpIPositions
        const { [layer]: lrMatches } = matches

        for (const node of nodes) {
          const fields = nodeFields.get(node)
          fields.set("type", nType)

          const nodeIPositions = iPos.get(node)
          const nodeMatches =
            lrMatches == null || !lrMatches.has(node)
              ? new Set()
              : lrMatches.get(node)
          const { spans, tip } = this.getHLText(
            nodeIPositions, nodeMatches, text, valueMap,
          )
          const tipRep = (tip == null) ? "" : `(=${tip})`

          let piece = ""
          for (const [hl, val] of spans) {
            piece += `${hl ? "«" : ""}${val}${hl ? "»" : ""}${tipRep}`
          }
          fields.set(tpLayer, piece)
        }
      }
    }

    const headLine = `node\t${headFields.join("\t")}\n`
    const lines = [headLine]

    for (let i = 0; i < ntypes.length; i++) {
      const nType = ntypes[i]
      const { [nType]: { nodes } } = tpResults
      if (nodes == null) {
        continue
      }

      const sortedNodes = [...nodes].sort()

      for (const node of sortedNodes) {
        const num = nodeseq ? node - ntypesinit[nType] + 1 : node
        const line = [`${num}`]
        const fields = nodeFields.has(node) ? nodeFields.get(node) : new Map()

        for (const headField of headFields) {
          line.push(fields.has(headField) ? fields.get(headField) : "")
        }
        lines.push(`${line.join("\t")}\n`)
      }
    }

    return lines
  }

  saveResults() {
    /* save job results to file
     * The file will be offered to the user as a download
     */
    const { Disk, State } = this

    const { jobName } = State.gets()
    const lines = this.tabular()
    const text = lines.join("")
    Disk.download(text, jobName, "tsv", true)
  }

}

/* --- APPLICATION CHAPTER ----------------------------------------------
 */

class StateProvider {
/* THE STATE
 *
 * The state contains changeable information needed to present the
 * interface.
 * It contains two kinds of information:
 *   - computed search results
 *   - user interaction state (button clicks, field entries)
 *
 * For a description of the state members, see the class definition below.
 *
 * MUTABLE STATE
 *
 * Contrary React-Redux practice, our state is mutable.
 * We do not work with cycles that re-render the display after state changes,
 * so we do not need to detect state changes efficiently.
 * Instead, at each state change, we also update the interface.
 *
 * STATE PROVIDER OBJECT
 *
 * The state logic is encapsulated in a class which is instantiated
 * with one object, whose data represents the state of the app.
 *
 * INITIAL STATE
 *
 * The jobState part of the data is fixed in shape.
 * The State Provider furnish a jobState that has all members and submembers present,
 * filled with default values, none of which are missing or null.
 *
 * The jobState can be initialized from external, incoming data,
 * use the startj method for that.
 *
 * SAFE MERGE
 *
 * The jobState may come from untrusted sources, such as an imported file
 * of localStorage. Such a jobState may not conform to the shape of the jobState
 * as prescribed here.
 * So the Provider performs a safe merge of the new jobState into a
 * fresh initial jobState.
 * A safe merge copies leaf members of the incoming state into corresponding places
 * in the initial state, provided the path in the incoming state exists in the initial
 * state, and the type of the value in the incoming state is the same as that of
 * the corresponding value in the initial state, and the incoming value is not null.
 * If the type of the value is string, the value should be less than MAXINPUT.
 *
 * If any of these conditions are not met, the update of that value is skipped.
 * An error message will be written to the console .
 *
 * GETTING the state
 *
 * Always by the gets() or getj() methods
 *
 * gets is for top level state slices except jobState
 * sets gets the jobState slice as a deep copy (so you cannot modify the jobState)
 *
 * const { query: { [nType]: { [layer]: pattern } } } = State.getj()
 *
 * N.B. We do not have to take care to use default values ( = {} ) for intermediate
 * subobjects, because the members of the jobState are guaranteed to exist.
 *
 * SETTING the state
 *
 * Always by the sets() or setj() methods
 *
 * We get the members of state object back (except jobState).
 * This enables patterns where we set a state member
 * and then use that value in a local variable:
 *
 * const { tpResults } = State.sets({ tpResults: {} })
 *
 * Note that setj() does not return data!
 *
 * When setting the jobState with setj(),
 * we apply the same checks as when we start a job from external data.
 *
 * INVARIANT:
 *
 * The jobState always has the full prescribed shape, with all members present at any
 * level, and with now leaf values null.
 */

  /* private members
   */

  deps({ Log, Mem, Config }) {
    this.Log = Log
    this.Mem = Mem
    this.Config = Config
  }

  init() {
    /* Make the contents for an initial, valid state, with defaults filled in
     * It can be called when certain elements of the state change.
     */

    this.data = {
      /* for each node type: { nodes, matches }
       * nodes: the set of nodes that match the query
       * - they match all layers of this node type,
       * - when you project the nodes to other node types,
       *   the projected nodes match all layers of those types as well
       * matches: for each layer of this type:
       * - the mapping from nodes to matched character positions
       */
      tpResults: null,

      /* array of results
       * when a composeType is chosen, we generate a table of results from tpResults
       * A result consists of
       * - a node of the containerType: the result node
       * - its ancestor nodes from higher type
       * - all of its descendent nodes in lower types.
       * A result only contains the nodes, not yet actual matched text.
       * In order to render the results table, we need both
       * tpResults and resultsComposed
       */
      resultsComposed: null,

      /* a mapping of nodes to node types,
       * for all nodes that occur in rendered results
       * including non-matching descendants of matching container nodes
       */
      resultTypeMap: null,

      /* the name of the current job
       * The current search session is called a "job".
       * When we store a jobState in localStorage, we use its name as key.
       * When we store a jobState on file, we use its name as file name.
       */
      jobName: null,

      /* the current state of all user interactions
       * The jobState is what gets serialized when we store/retrieve jobs,
       * whether in localStorage or in files.
       * See for the members the definition of jobState below.
       */
      jobState: this.initjslice(),
    }
  }

  initjslice() {
    /* Make the contents for an initial, valid jobState, with defaults filled in
     * This is the first step in guaranteeing that the jobState has a fixed shape.
     */
    const { Config: { ntypes, containerType, layers, visible } } = this

    /* First set a dumb, superficial value
     */
    const jobState = {
      /* options that affect general aspects of searching
       */
      settings: {
        /* whether to run search immediately after change or after button press
         */
        autoexec: true,
        /* whether displayed node numbers start at 1 per node type
         * or are exactly the TF node numbers
         */
        nodeseq: true,
      },

/* https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
 */
      /* { pattern, flags, exec } per node type and then per layer
       * - pattern: a regex (regular expression): defines the search
       * - flags: (i m s)
       * - exec: whether it is will be/is executed
       */
      query: {},

      /* whether the results in the state are out of sync with the pattern
       * This becomes true when a user edits the search patterns
       * but has not yet executed the new query
       */
      dirty: false,

      /* per node type whether its layers are expanded.
       * Not expanded means: only the active layers are visible.
       * A layer is active if
       * - it has a non-empty pattern or
       * - its visible flag is set
       */
      expandTypes: {},

      /* the node type used for composing results
       */
      containerType,

      /* per node type and layer whether the layer is visible in the results
       */
      visibleLayers: {},

      /* the current position in the table of results
       * this result is drawn in the middle of the screen if possible
       * The focused result will be marked strongly on the interface.
       * Special values:
       * * -2: query has not been executed
       * * -1: query has been executed and has 0 results
       * *  0: query has been executed, there are results, focus on first result
       */
      focusPos: -2,

      /* the previous focusPos.
       * The result at this position will be marked lightly.
       */
      prevFocusPos: -2,
    }

    /* Now create deeper values, from Config defaults
     */
    const { query, expandTypes, visibleLayers } = jobState

    for (const nType of ntypes) {
      const { [nType]: tpInfo = {} } = layers
      const { [nType]: tpVisible = {} } = visible

      query[nType] = {}
      expandTypes[nType] = false
      visibleLayers[nType] = { _: false }

      for (const layer of Object.keys(tpInfo)) {
        const { [layer]: { pattern = "" } = {} } = tpInfo
        const { [layer]: lrVisible = false } = tpVisible

        query[nType][layer] = {
          pattern: DEBUG ? pattern : "",
          flags: { ...FLAGSDEFAULT },
          exec: true,
        }
        visibleLayers[nType][layer] = lrVisible
      }
    }
    return jobState
  }
  startjslice(incoming) {
    /* create a starting jobState out of an incoming jobState,
     * which is safely merged into an initial jobState
     */
    const { data } = this

    const freshJobState = this.initjslice()
    this.merge(freshJobState, incoming, [])
    data.jobState = freshJobState
  }

  /* public members
   */

  gets() {
    /* GET STATE
     *
     * returns a shallow copy of the state, but only with the non jobState
     * members.
     * Note that the caller cannot use this to change the members
     * that are string or number.
     * But he can change the contents of the members that hold an object as value.
     * This is intentional.
     */
    const { data: { jobState, ...rest } } = this
    return rest
  }

  getjn() {
    /* GET JOB NAME
     * convenience function
     */
    const { data: { jobName } } = this
    return jobName
  }

  sets(incoming) {
    /* SET STATE
     *
     * update the state by means of an object data containing the updates
     * The structure of the updates reflects the structure of a (part of) the state,
     * only at top-level.
     *
     * If the part jobName or jobState is affected, the jobState is committed to
     * localStorage
     */
    const { Log, Mem, data } = this

    let commit = false

    for (const [inKey, inValue] of Object.entries(incoming)) {
      const stateVal = data[inKey]
      if (stateVal === undefined) {
        Log.error(`state update: unknown key ${inKey}`)
        continue
      }
      data[inKey] = inValue
      if (inKey == "jobName" || inKey == "jobState") {
        commit = true
      }
    }
    if (commit) {
      const { jobName, jobState } = data
      Mem.setk(jobName, jobState)
    }
    return this.gets()
  }

  startj(jobIn, jobStateIn) {
    /* INIT JOB STATE
     *
     * updates the state for a new, named job with incoming data
     * The jobState is committed to Mem
     */
    const { Mem, data } = this
    const jobName = jobIn || DEFAULTJOB

    data.jobName = jobName
    this.startjslice(jobStateIn)
    const { jobState } = data
    Mem.setk(jobName, jobState)
  }

  getj() {
    /* GET JOB STATE
     *
     * returns the jobState
     * The caller should not modify the jobState, so we return a deep copy of it
     */
    const { data: { jobState } } = this
    return JSON.parse(JSON.stringify(jobState))
  }

  setj(incoming) {
    /* SET JOB STATE
     *
     * Performs a safe update of the jobState by incoming data
     * The jobState is committed to Mem
     */
    const { Mem, data: { jobName, jobState } } = this
    this.merge(jobState, incoming, [])
    Mem.setk(jobName, jobState)
  }

  /* auxiliary functions for state operations
   */

  merge(orig, incoming, path) {
    /* Merge an incoming object safely into an original object.
     * The shape of orig will not be altered
     *  1. no new keys will be introduced at any level
     *  2. no value becomes undefined or null
     *  3. no value changes type
     *  4. no value becomes too long
     *
     * For all violations, an error message is sent to the console .
     *
     * Invariant: orig is an object, not a leaf value
     */

    const { Log } = this
    const pRep = `Merge: incoming at path "${path.join(".")}": `

    if (incoming == null) {
      Log.error(`${pRep}undefined`)
      return
    }
    if (!(typeof incoming === OBJECT && !Array.isArray(incoming))) {
      Log.error(`${pRep}non-object`)
      return
    }
    for (const [inKey, inValue] of Object.entries(incoming)) {
      const origValue = orig[inKey]
      if (origValue === undefined) {
        Log.error(`${pRep}unknown key ${inKey}`)
        continue
      }
      if (inValue == null) {
        Log.error(`${pRep}undefined value for ${inKey}`)
        continue
      }
      const origType = typeof origValue
      const inType = typeof inValue
      if (origType === NUMBER || origType === STRING || origType === BOOL) {
        if (inType === OBJECT) {
          const repVal = JSON.stringify(inValue)
          Log.error(`${pRep}object ${repVal} for ${inKey} instead of leaf value`)
          continue
        }
        if (inType != origType) {
          Log.error(`${pRep}type conflict ${inType}, expected ${origType} for ${inKey}`)
          continue
        }
        if (inType === STRING && inValue.length > MAXINPUT) {
          const eRep = `${inValue.length} (${inValue.substr(0, 20)} ...)`
          Log.error(`${pRep}maximum length exceeded for ${inKey}: ${eRep}`)
          continue
        }

        /* all is well, we replace the value in orig by the incoming value
         */
        orig[inKey] = inValue
        continue
      }
      if (origType !== OBJECT) {
        Log.error(
          `${pRep}unknown type ${inType} for ${inKey}=${inValue} instead of object`
        )
        continue
      }
      if (origType === OBJECT) {
        if (inType !== OBJECT) {
          Log.error(`${pRep}leaf value {inValue} for {inKey} instead of object`)
          continue
        }
        this.merge(origValue, inValue, [...path, inKey])
      }
    }
  }
}

class JobProvider {
/* JOB CONTROL
 *
 * Jobs correspond to search sessions. The current job lives in the state,
 * as a member called "jobState".
 *
 * The user can make new jobs, duplicate them, rename them, kill them, switch
 * between them, save them as file, load them from file.
 *
 * All jobs that the apps loads, will be saved in localStorage.
 * Each action that changes the jobState, triggers a save action into
 * localStorage.
 */

/* Starting
 *
 * When we start up we look in localStorage for the last job.
 * If we find that, we load its data into the jobState part of the state.
 *
 * If not, we derive an initial jobState from State, and load that
 * into the state
 */

  deps({ Disk, Mem, State, Gui }) {
    this.Disk = Disk
    this.Mem = Mem
    this.State = State
    this.Gui = Gui
  }

  init() {
    /* Lookup last job from local storage, if any,
     * or else use init settings from State
     */
    const { Mem, State } = this

    const [jobName, jobContent] = Mem.getkl()
    State.startj(jobName, jobContent)
  }

  later() {
    /* Initialize the GUI for this Job
     * This might include performing a search
     * so we do this later, after the corpus has loaded
     */
    const { Gui } = this

    Gui.applyJob(true)
  }

  /* job actions as defined by controls on the interface
   *
   * All these actions have to take care of
   *
   * - updating the state
   * - applying the new state to the interface
   * - storing the new state in local storage
   */

  list() {
    /* list of all remembered jobs
     */
    const { Mem } = this
    return Mem.keys()
  }

  make(newJob) {
    /* make a fresh job
     */
    const { State, Gui } = this
    const { jobName } = State.gets()

    if (jobName == newJob) {
      return
    }
    State.startj(newJob, {})
    Gui.applyJob(true)
  }

  copy(newJob) {
    /* copy current job to a new name
     */
    const { State, Gui } = this
    const { jobName } = State.gets()

    if (jobName == newJob) {
      return
    }
    State.sets({ jobName: newJob })
    Gui.applyJob(false)
  }

  rename(newJob) {
    /* rename current job
     */
    const { Mem, State, Gui } = this
    const { jobName } = State.gets()

    if (jobName == newJob) {
      return
    }
    Mem.remk(jobName)
    State.sets({ jobName: newJob })
    Gui.applyJob(false)
  }

  kill() {
    /* kill (=delete) current job
     * But only if there is still a job left,
     * otherwise rename to the default name
     */
    const { Mem, State } = this
    const { jobName } = State.gets()

    const newJob = Mem.remk(jobName)
    this.change(newJob)
  }

  change(jobName) {
    /* switch to selected job
     */
    const { Mem, State, Gui } = this

    const jobContent = Mem.getk(jobName)
    State.startj(jobName, jobContent)
    Gui.applyJob(true)
  }

  read(elem) {
    /* produce a handler for reading an uploaded file
     */
    const { Disk, State, Gui } = this

    const handler = (fileName, ext, content) => {
      if (ext != ".json") {
        alert(`${fileName}${ext} is not a JSON file`)
        return
      }
      const jobContent = JSON.parse(content)
      State.startj(fileName, jobContent)
      Gui.applyJob(true)
      Gui.applyJobs()
    }
    Disk.upload(elem, handler)
  }

  write() {
    /* save current job state to file
     * The file will be offered to the user as a download
     */
    const { State, Disk } = this

    const { jobName } = State.gets()
    const jobState = State.getj()

    const text = JSON.stringify(jobState)
    Disk.download(text, jobName, "json", false)
  }
}

class GuiProvider {
/* INITIALIZE DYNAMIC PARTS OF THE INTERFACE
 *
 * Almost everything on the interface is depending on the data
 * that is encountered in Config
 * Here we generate HTML and place it in the DOM
 */

  deps({ State, Job, Config, Search }) {
    this.State = State
    this.Job = Job
    this.Config = Config
    this.Search = Search
  }

  init() {
    this.build()
    this.activateJobs()
    this.activateSearch()
  }

  /* BUILDING the HTML
   */

  build() {
    /* fill in title and description
     */
    const {
      Config: {
        ntypesR, description, captions: { title }, layers, levels,
      },
    } = this
    $("head>title").html(title)
    $("#title").html(title)
    $("#description").html(description)
    $("go").html(SEARCH.dirty)

    /* Generate all search controls
     * and put them on the interface
     */

    const querybody = $("#querybody")
    const html = []

    for (const nType of ntypesR) {
      const tpInfo = layers[nType] || {}
      const description = levels[nType] || {}
      html.push(this.genTypeWidgets(nType, description, tpInfo))
    }
    querybody.html(html.join(""))

    this.placeStatTotals()
    this.placeSettings()
  }

  placeSettings() {
    const { State } = this
    const { settings } = State.getj()

    const html = []

    for (const name of Object.keys(settings)) {
      html.push(`
        <p><button
          type="button" name="${name}" class="expand on"
        ></button></p>
      `)
    }
    const settingsplace = $("#settings")
    settingsplace.html(html.join(""))
  }

  placeStatTotals() {
    /* stats
     */
    const { Config: { ntypesR, ntypessize } } = this

    const html = []

    for (const nType of ntypesR) {
      const total = ntypessize[nType]
      html.push(`
  <tr>
    <td><span class="statlabel">${nType}</span></td>
    <td class="stat"><span class="stattotal">${total}</span></td>
    <td class="stat"><span class="statresult" ntype="${nType}"></span></td>
  </tr>
  `)
    }
    const statsbody = $("#statsbody")
    statsbody.html(html.join(""))
  }

  placeStatResults(stats) {
    /* draw statistics found by weed() on the interface
     */
    const { Config: { ntypes } } = this

    for (const nType of ntypes) {
      const dest = $(`.statresult[ntype="${nType}"]`)
      const stat = stats[nType]
      const useStat = (stat == null) ? " " : stat
      dest.html(`${useStat}`)
    }
  }

  genTypeWidgets(nType, description, tpInfo) {
    /* Generate html for the search controls for a node type
     */
    const nTypeRep = description
      ? `<details>
           <summary class="lv">${nType}</summary>
           <div>${description}</div>
          </details>`
      : `<span class="lv">${nType}</span>`

    const html = []
    html.push(`
  <tr class="qtype" ntype="${nType}">
    <td class="lvcell">${nTypeRep}</td>
    <td><button type="button" name="expand" class="expand"
      ntype="${nType}"
      title="${TIP.expand}"
    ></button></td>
    <td><button type="button" name="ctype" class="unit"
      ntype="${nType}"
      title="${TIP.unit}"
    >result</button></td>
    <td></td>
    <td><button type="button" name="visible" class="visible"
      ntype="${nType}" layer="_"
      title="${TIP.visibletp}"
    ></button></td>
  </tr>
  `)

    for (const [layer, lrInfo] of Object.entries(tpInfo)) {
      html.push(this.genWidget(nType, layer, lrInfo))
    }
    return html.join("")
  }

  genWidget(nType, layer, lrInfo) {
    /* Generate html for the search controls for a single layer
     */
   return (
    `
  <tr class="ltype" ntype="${nType}" layer="${layer}">
    <td>${this.genLegend(nType, layer, lrInfo)}</td>
    <td>
      /<input type="text" kind="pattern" class="pattern"
        ntype="${nType}" layer="${layer}"
        maxlength="${MAXINPUT}"
        value=""
      ><span kind="error" class="error"
        ntype="${nType}" layer="${layer}"
      ></span>/</td>
    <td><button type="button" name="i" class="flags"
        ntype="${nType}" layer="${layer}"
        title="${TIP.flagi}"
      >i</button><button type="button" name="m" class="flags"
        ntype="${nType}" layer="${layer}"
        title="${TIP.flagm}"
      >m</button><button type="button" name="s" class="flags"
        ntype="${nType}" layer="${layer}"
        title="${TIP.flags}"
      >s</button>
    </td>
    <td><button type="button" name="exec" class="exec"
      ntype="${nType}" layer="${layer}"
      title="${TIP.exec}"
    ></button></td>
    <td><button type="button" name="visible" class="visible"
      ntype="${nType}" layer="${layer}"
      title="${TIP.visible}"
    ></button></td>
  </tr>
  `)
  }

  genLegend(nType, layer, lrInfo) {
    /* Generate html for the description / legend of a single layer
     */
    const { valueMap, description } = lrInfo
    const html = []

    if (valueMap || description) {
      html.push(`
  <details>
    <summary class="lyr">${layer}</summary>
  `)
      if (description) {
        html.push(`<div>${description}</div>`)
      }
      if (valueMap) {
        for (const [acro, full] of Object.entries(valueMap)) {
          html.push(`
  <div class="legend">
    <b><code>${acro}</code></b> =
    <i><code>${full}</code></i>
  </div>`
          )
        }
      }
      html.push(`
  </details>
  `)
    } else {
      html.push(`
  <span class="lyr">${layer}</span>
  `)
    }
    return html.join("")
  }


  /* MAKE THE INTERFACE ACTIVE
   *
   * Add actions to the controls of the search interface,
   * including those for navigating the results
   */

  /* ADDING ACTIONS TO THE DOM
   */

  activateJobs() {
    /* make all job controls active
     */
    const { State, Job } = this

    const jobnew = $("#newj")
    const jobdup = $("#dupj")
    const jobrename = $("#renamej")
    const jobkill = $("#deletej")
    const jobchange = $("#jchange")

    jobnew.off("click").click(() => {
      /* make brand new job with no data, ask for new name
       */
      const newJob = this.suggestName(null)
      if (newJob == null) {
        return
      }
      Job.make(newJob)
      this.applyJobs()
      this.clearBrowserState()
    })
    jobdup.off("click").click(() => {
      /* duplicate current job, ask for related new name
       */
      const { jobName } = State.gets()
      const newJob = this.suggestName(jobName)
      if (newJob == null) {
        return
      }
      Job.copy(newJob)
      this.applyJobs()
      this.clearBrowserState()
    })
    jobrename.off("click").click(() => {
      /* rename current job, ask for related new name
       */
      const { jobName } = State.gets()
      const newJob = this.suggestName(jobName)
      if (newJob == null) {
        return
      }
      Job.rename(newJob)
      this.applyJobs()
      this.clearBrowserState()
    })
    jobkill.off("click").click(() => {
      /* kill current job
       */
      Job.kill()
      this.applyJobs()
      this.clearBrowserState()
    })
    jobchange.change(e => {
      /* switch to another job
       */
      const { jobName } = State.gets()
      const newJob = e.target.value
      if (jobName == newJob) {
        return
      }
      Job.change(newJob)
      this.clearBrowserState()
    })

    /* import job button
     */

    const fileSelect = $("#importj")
    const fileElem = $("#imjname")

    fileSelect.off("click").click(e => {
      fileElem.click()
      e.preventDefault()
    })

    fileElem.off("change").change(e => Job.read(e.target))

    /* export job button
     */

    const expjButton = $("#exportj")
    expjButton.off("click").click(() => {
      Job.write()
    })

    /* populate the list of known options
     */
    this.applyJobs()
  }

  suggestName(jobName) {
    /* ask for a new name for a job
     * Given jobName, we append an `N` until the name is not one of the known jobs.
     * This is only a suggestion, the user may override it.
     * But if jobName is null, the first new name will be taken straightaway
     * without user interaction.
     */
    const { Job } = this

    const jobNames = new Set(Job.list())
    let newName = jobName
    const resolved = s => s && s != jobName && !jobNames.has(s)
    let cancelled = false
    while (!resolved(newName) && !cancelled) {
      while (!resolved(newName)) {
        if (newName == null) {
          newName = DEFAULTJOB
        } else {
          newName += "N"
        }
      }
      if (jobName != null) {
        const answer = prompt("New job name:", newName)
        if (answer == null) {
          cancelled = true
        } else {
          newName = answer
        }
      }
    }
    return cancelled ? null : newName
  }

  activateSearch() {
    /* make the search button active
     */
    const { State, Search } = this

    const go = $(`#go`)

    const handleQuery = e => {
      e.preventDefault()
      go.off("click")
      Search.runQuery()
      State.setj({ dirty: false })
      this.clearBrowserState()
      go.click(handleQuery)
    }

    go.off("click").click(handleQuery)
    /* handle changes in the expansion of layers
     */

    const settingctls = $("#settings button")
    settingctls.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const name = elem.attr("name")
      const isNo = elem.hasClass("no")
      if (!isNo) {
        const isOn = elem.hasClass("on")
        State.setj({ settings: { [name]: !isOn } })
        this.applySettings(name)
        if (name == "nodeseq") {
          Search.displayResults()
        }
      }
      this.clearBrowserState()
    })

    const expands = $(`button[name="expand"]`)
    expands.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const isNo = elem.hasClass("no")
      if (!isNo) {
        const isOn = elem.hasClass("on")
        State.setj({ expandTypes: { [nType]: !isOn } })
        this.applyLayers(nType)
      }
      this.clearBrowserState()
    })
    /* handle changes in the container type
     */
    const units = $(`button[name="ctype"]`)
    units.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const { containerType } = State.getj()
      if (nType == containerType) {
        return
      }
      State.setj({ containerType: nType })
      Search.composeResults(true)
      Search.displayResults()
      this.applyUnits(nType)
      this.clearBrowserState()
    })
    /* handle changes in the search patterns
     */
    const patterns = $(`input[kind="pattern"]`)
    patterns.off("change").change(e => {
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const { target: { value: pattern } } = e
      this.makeDirty(elem)
      State.setj({ query: { [nType]: { [layer]: { pattern } } } })

      const { settings: { autoexec } } = State.getj()
      if (autoexec) {
        Search.runQuery()
      }
      this.applyExec(nType, layer)
      this.clearBrowserState()
    })
    const errors = $(`[kind="error"]`)
    errors.hide()
    /* handle changes in the regexp flags
     */
    const flags = $(`button.flags`)
    flags.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const name = elem.attr("name")
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const isOn = elem.hasClass("on")
      this.makeDirty(elem)
      State.setj({ query: { [nType]: { [layer]: { flags: { [name]: !isOn } } } } })

      const { settings: { autoexec } } = State.getj()
      if (autoexec) {
        Search.runQuery()
      }
      this.setButton(name, `[ntype="${nType}"][layer="${layer}"]`, !isOn)
      this.clearBrowserState()
    })
    /* handles changes in the "exec" controls
     */
    const execs = $(`button.exec`)
    execs.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const isNo = elem.hasClass("no")
      if (!isNo) {
        const isOn = elem.hasClass("on")
        this.makeDirty(elem)
        State.setj({ query: { [nType]: { [layer]: { exec: !isOn } } } })

        const { settings: { autoexec } } = State.getj()
        if (autoexec) {
          Search.runQuery()
        }
        this.setButton("exec", `[ntype="${nType}"][layer="${layer}"]`, !isOn, true)
      }
      this.clearBrowserState()
    })
    /* handles changes in the "visible" controls
     */
    const visibles = $(`button.visible`)
    visibles.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const isOn = elem.hasClass("on")
      State.setj({ visibleLayers: { [nType]: { [layer]: !isOn } } })
      this.setButton(
        "visible", `[ntype="${nType}"][layer="${layer}"]`, !isOn, true,
      )
      Search.displayResults()
      this.clearBrowserState()
    })

    /* handles display of search results
     */
    this.activateResults()

    /* handles export of search results
     */
    const exprButton = $("#exportr")
    exprButton.off("click").click(() => {
      const { tpResults } = State.gets()
      if (tpResults == null) {
        alert("Query has not been executed yet")
        return
      }

      Search.saveResults()
    })
  }

  makeDirty(elem) {
    const { State } = this

    const go = $("#go")
    const expr = $("#exportr")
    elem.addClass("dirty")
    go.addClass("dirty")
    go.html(SEARCH.dirty)
    expr.removeClass("active")
    State.setj({ dirty: true })
  }

  activateResults() {
    /* make the number controls active
     *   the result slider
     *   the input box for the focus position
     * Keep the various ways of changing the focus position synchronized
     */
    const { State, Search } = this

    const slider = $("#slider")
    const setter = $("#setter")
    const minp = $("#minp")
    const min2p = $("#min2p")
    const mina = $("#mina")
    const maxp = $("#maxp")
    const max2p = $("#max2p")
    const maxa = $("#maxa")

    slider.off("change").change(() => {
      const { focusPos } = State.getj
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(slider.val() - 1),
      })
      Search.displayResults()
    })
    setter.off("change").change(() => {
      const { focusPos } = State.getj
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(setter.val() - 1),
      })
      Search.displayResults()
    })
    minp.off("click").click(() => {
      const { focusPos } = State.getj
      if (focusPos == null) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos - 1),
      })
      Search.displayResults()
    })
    min2p.off("click").click(() => {
      const { focusPos } = State.getj
      if (focusPos == null) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos - QUWINDOW),
      })
      Search.displayResults()
    })
    mina.off("click").click(() => {
      const { focusPos } = State.getj
      if (focusPos == null) {
        return
      }
      State.setj({ prevFocusPos: focusPos, focusPos: 0 })
      Search.displayResults()
    })
    maxp.off("click").click(() => {
      const { focusPos } = State.getj
      if (focusPos == null) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos + 1),
      })
      Search.displayResults()
    })
    max2p.off("click").click(() => {
      const { focusPos } = State.getj
      if (focusPos == null) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos + QUWINDOW),
      })
      Search.displayResults()
    })
    maxa.off("click").click(() => {
      const { focusPos } = State.getj
      if (focusPos == null) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(-1),
      })
      Search.displayResults()
    })
  }

  /* APPLYING STATE CHANGES to the DOM
   */

  applyJob(run) {
    /* apply jobState to the interface
     *
     * try to run the query if parameter run is true
     */
    const { Config, State } = this

    const { ntypes, layers } = Config

    const { query, containerType, visibleLayers } = State.getj()

    this.applyJobs()

    this.applySettings()

    for (const nType of ntypes) {
      const { [nType]: tpInfo = {} } = layers
      const { [nType]: tpQuery } = query
      const { [nType]: tpVisible } = visibleLayers

      this.applyLayers(nType)

      const { _: visibleNodes } = tpVisible
      this.setButton("visible", `[ntype="${nType}"][layer="_"]`, visibleNodes, true)

      for (const layer of Object.keys(tpInfo)) {
        const { [layer]: { pattern, flags } } = tpQuery
        const box = $(`[kind="pattern"][ntype="${nType}"][layer="${layer}"]`)
        box.val(pattern)

        const useFlags = { ...FLAGSDEFAULT, ...flags }
        for (const [flag, isOn] of Object.entries(useFlags)) {
          this.setButton(flag, `[ntype="${nType}"][layer="${layer}"]`, isOn)
        }

        this.applyExec(nType, layer)

        const { [layer]: visible } = tpVisible
        this.setButton(
          "visible", `[ntype="${nType}"][layer="${layer}"]`, visible, true,
        )
      }
    }
    this.applyUnits(containerType)
    this.applyResults(run)
    this.clearBrowserState()
  }

  applyExec(nType, layer) {
    const { State } = this

    const { query: { [nType]: { [layer]: { pattern, exec } } } } = State.getj()
    const useExec = pattern.length == 0 ? null : exec
    this.setButton("exec", `[ntype="${nType}"][layer="${layer}"]`, useExec, true)
  }

  applyJobs() {
    /* populate the options of the select box with the remembered jobs in localStorage
     */
    const { Job, State } = this
    const { jobName } = State.gets()
    const jobchange = $("#jchange")
    const jobname = $("#jobname")

    let html = ""
    for (const otherJobName of Job.list()) {
      const selected = otherJobName == jobName ? " selected" : ""
      html += `<option value="${otherJobName}"${selected}>${otherJobName}</option>`
      jobchange.html(html)
    }
    jobchange.val(jobName)
    jobname.val(jobName)
  }

  applySettings(name) {
    const { State } = this

    const { settings } = State.getj()

    const tasks = (name == null) ? Object.entries(settings) : [[name, settings[name]]]

    for (const [name, setting] of tasks) {
      this.setButton(name, "", setting, true)
    }
  }

  applyLayers(nType) {
    const { Config: { layers: { [nType]: tpLayers = {} } = {} }, State } = this
    const {
      expandTypes: { [nType]: expand },
      visibleLayers: { [nType]: tpVisible },
      query: { [nType]: tpQuery },
    } = State.getj()

    const totalLayers = Object.keys(tpLayers).length
    const useExpand = (totalLayers == 0) ? null : expand

    let totalActive = 0

    for (const layer of Object.keys(tpLayers)) {
      const row = $(`.ltype[ntype="${nType}"][layer="${layer}"]`)
      const { [layer]: { pattern } } = tpQuery
      const { [layer]: visible } = tpVisible
      const isActive = visible || pattern.length > 0

      if (isActive) {
        totalActive += 1
      }
      if (expand || isActive) {
        row.show()
      }
      else {
        row.hide()
      }
    }
    const { expand: { no, on, off } } = BUTTON
    const expandText = {
      no,
      on: `${on}(${totalActive})`,
      off: `${off}(${totalLayers})`,
    }
    this.setButton("expand", `[ntype="${nType}"]`, useExpand, expandText)
  }

  applyUnits(containerType) {
    /* update the tags on the buttons for the containerType selection
     * Only one of them can be on, they are function-wise radio buttons
     */
    const { Config: { ntypes, ntypesI } } = this

    const containerIndex = ntypesI.get(containerType)
    for (const nType of ntypes) {
      const nTypeIndex = ntypesI.get(nType)
      const k = (containerIndex == nTypeIndex)
        ? "r" : (containerIndex < nTypeIndex)
        ? "a" : "d"
      const elem = $(`button[name="ctype"][ntype="${nType}"]`)
      elem.html(UNITTEXT[k])
    }
    this.setButton("ctype", ``, false)
    this.setButton("ctype", `[ntype="${containerType}"]`, true)
  }

  applyResults(run) {
    /* fill in the results of a job
     * We will run the query first if all of the following conditions are met:
     * - parameter run = true.
     * - the query is not empty
     * Otherwise, we clear all result components in the state.
     */
    // const { State, Search } = this
    const { Search } = this

    if (run) {
      Search.runQuery()
    }
  }

  applyFocus() {
    /* adjust the interface to the current focus
     * Especially the result navigation controls and the slider
     */
    const { State } = this

    const { resultsComposed } = State.gets()
    const { focusPos } = State.getj()
    const setter = $("#setter")
    const setterw = $("#setterw")
    const slider = $("#slider")
    const sliderw = $("#sliderw")
    const total = $("#total")
    const totalw = $("#totalw")
    const minp = $("#minp")
    const min2p = $("#min2p")
    const mina = $("#mina")
    const maxp = $("#maxp")
    const max2p = $("#max2p")
    const maxa = $("#maxa")
    const nResults = resultsComposed == null ? 0 : resultsComposed.length
    const nResultsP = Math.max(nResults, 1)
    const stepSize = Math.max(Math.round(nResults / 100), 1)
    const focusVal = focusPos == -2 ? 0 : focusPos + 1
    const totalVal = focusPos == -2 ? 0 : nResults
    setter.attr("max", nResultsP)
    setter.attr("step", stepSize)
    slider.attr("max", nResultsP)
    slider.attr("step", stepSize)
    setter.val(focusVal)
    slider.val(focusVal)
    total.html(totalVal)

    sliderw.hide()
    setterw.hide()
    totalw.hide()
    minp.removeClass("active")
    min2p.removeClass("active")
    mina.removeClass("active")
    maxp.removeClass("active")
    max2p.removeClass("active")
    maxa.removeClass("active")

    if (focusPos != -2) {
      setterw.show()
      totalw.show()
      if (nResults > 2 * QUWINDOW) {
        sliderw.show()
      }
      if (focusPos < nResults - 1) {
        maxa.addClass("active")
        maxp.addClass("active")
      }
      if (focusPos + QUWINDOW < nResults - 1) {
        max2p.addClass("active")
      }
      if (focusPos > 0) {
        mina.addClass("active")
        minp.addClass("active")
      }
      if (focusPos - QUWINDOW > 0) {
        min2p.addClass("active")
      }
    }

    /* scrolls the interface to the result that is in focus
     */
    const rTarget = $(`.focus`)
    if (rTarget != null && rTarget[0] != null) {
      rTarget[0].scrollIntoView({ block: "center", behavior: "smooth" })
    }
  }

  /* auxiliary methods
   */

  setButton(name, spec, onoff, changeTag) {
    /* Put a button in an on or off state
     * name is what is in their "name" attribute,
     * with spec you can pass additional selection criteria,
     * as a jQuery selector
     * onoff is true or false: true will add the class on, false will remove that class
     * changeTag: modify the tags on the button
     * - if true: pick up the tags from the constant BUTTON, indexed by name
     * - if an object: pick up the texts directly from this object
     * in both cases we expect texts for keys "no", "on", "off"
     * Which one is chosen, depends on onoff: null, true, false
     */
    const elem = $(`button[name="${name}"]${spec}`)
    if (onoff == null) {
      elem.removeClass("on")
      elem.addClass("no")
    }
    else {
      if (onoff) {
        elem.addClass("on")
        elem.removeClass("no")
      }
      else {
        elem.removeClass("on")
        elem.removeClass("no")
      }
    }
    if (changeTag) {
      const texts = (typeof changeTag == BOOL) ? BUTTON[name] : changeTag
      elem.html(texts[(onoff == null) ? "no" : onoff ? "on" : "off"])
    }
  }

  checkFocus(focusPos) {
    /* take care that the focus position is always within
     * the correct range with respect to the number of results
     *
     * We implement here that going past the end of the results
     * will cycle back to the beginning and vice versa,
     * but only in step-by-step mode, not in screenful mode
     */
    const { State } = this

    const { resultsComposed } = State.gets()

    if (resultsComposed == null) {
      return -2
    }

    const nResults = resultsComposed.length
    if (focusPos == nResults) {
      return 0
    }
    if (focusPos == -1 || focusPos > nResults) {
      return nResults - 1
    }
    if (focusPos < 0) {
      return 0
    }
    return focusPos
  }

  clearBrowserState() {
    /* clears the browser state after a change in the form fields.
     * this prevents an "are you sure" - popup before reloading the page
     */
    if (window.history.replaceState) {
      window.history.replaceState(null, null, window.location.href)
    }
  }

}

/* --- SYSTEMS CHAPTER ----------------------------------------------
 */

class DiskProvider {
  /* FILE MANAGEMENT
   *
   * We cannot read from files and write to files directly from a browser script.
   *
   * When we want to read, we ask the user to point to a file,
   * and we "upload" that file
   * When we want to write, we offer a download to the user.
   */

  upload(elem, handler) {
    /* Reads the content of a file
     * Elem should be an <input type="file"> element
     * for which the user has selected a file already
     * After reading, handler is called
     * It should take fileName, extension and content as arguments
     * and so something business-logical with it
     */
    const { files } = elem
    if (files.length == 0) {
      alert("No file selected")
    } else {
      for (const file of files) {
        const reader = new FileReader()
        const [fileName, ext] = file.name.match(/([^/]+)(\.[^.]*$)/).slice(1)
        reader.onload = e => {
          handler(fileName, ext, e.target.result)
        }
        reader.readAsText(file)
      }
    }
  }

  download(text, fileName, ext, asUtf16) {
    /* collect data into a file for download
     * A downlaod will be prepared, with a given file name and extension.
     * The data is encoded as text in UTF-8 or in UTF-16
     */
    let blob

    if (asUtf16) {
      /* it turns out we need this clumsy detour via byte arrays
       * because otherwise the BOM mark will not be written correctly
       */
      const byteArray = []

      /* BOM Mark
       */
      byteArray.push(255, 254)

      /* Low level way to translate each uniocode character into 16 bits
       */
      for (let i = 0; i < text.length; ++i) {
        const charCode = text.charCodeAt(i)
        byteArray.push(charCode & 0xff)
        byteArray.push((charCode / 256) >>> 0)
      }

      blob = new Blob(
        [new Uint8Array(byteArray)], { type: "text/plain;charset=UTF-16LE;" }
      )
    } else {
      blob = new Blob([text], { type: "text/plain;charset=UTF-8;" })
    }
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.setAttribute("href", url)
    link.setAttribute("download", `${fileName}.${ext}`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

class MemProvider {
/* LOCAL STORAGE MANAGEMENT
 *
 * When we store/retrieve keys in localStorage,
 * we always prepend a prefix to the key:
 * - a fixed part, marking that it is a layered search app
 * - a Config dependent part: the name of the dataset
 *
 * We also store the last key used.
 * All content goes through JSON.stringify upon storing
 * and through JSON.parse upon retrieving.
 *
 * When retrieving content for non-existing keys, we silently return the empty object.
 *
 * localStorage for file:// urls is not clearly defined.
 * If several apps like this are being used in the same browser,
 * this practice will prevent collisions
 */

  /* private members
   */

  deps({ Config }) {
    this.Config = Config
  }

  init() {
    const { Config: { name: appName } } = this
    this.appPrefix = `ls/${appName}/`
    this.keyLast = `${this.appPrefix}LastJob`
    this.keyPrefix = `${this.appPrefix}Keys/`
    this.keyLength = this.keyPrefix.length
  }

  getRawKey(userKey) {return `${this.keyPrefix}${userKey}`}
  getUserKey(rawKey) {return rawKey.substring(this.keyLength)}
  getLastKey() {return localStorage.getItem(this.keyLast)}

  /* public members
   */

  getk(userKey) {
    /* retrieve stored content for a key
     *
     * Also store the key as last used key
     */
    localStorage.setItem(this.keyLast, userKey)
    const rawKey = this.getRawKey(userKey)
    return JSON.parse(localStorage.getItem(rawKey) ?? "{}")
  }

  setk(userKey, content) {
    /* stored content behind a key
     */
    const rawKey = this.getRawKey(userKey)
    localStorage.setItem(rawKey, JSON.stringify(content))
  }

  remk(userKey) {
    /* delete key and its stored content
     * If the key happens to be the last key,
     * remove the last key
     * return the last available key if any, else the default key
     */
    const rawKey = this.getRawKey(userKey)
    localStorage.removeItem(rawKey)
    const lastKey = this.getLastKey()
    if (userKey == lastKey) {
      localStorage.removeItem(this.keyLast)
    }
    const allKeys = this.keys()
    return (allKeys.length == 0) ? DEFAULTJOB : allKeys[allKeys.length - 1]
  }

  getkl() {
    /* retrieve stored content for the last key
     *
     * If there is no last key, take the last key
     * of all available keys, if any
     * and store that key as last key
     *
     * return both the key and the content
     */
    let lastKey = localStorage.getItem(this.keyLast)
    let content

    if (lastKey == null) {
      const allKeys = this.keys()
      if (allKeys.length == 0) {
        lastKey = DEFAULTJOB
        content = {}
        localStorage.setItem(this.keyLast, lastKey)
      }
      else {
        lastKey = allKeys[allKeys.length - 1]
        content = this.getk(lastKey)
      }
    }
    else {
      content = this.getk(lastKey)
    }
    return [lastKey, content]
  }

  setkl(userKey, content) {
    /* store content behind a key and make it the last key
     */
    this.setk(userKey, content)
    localStorage.setItem(this.keyLast, userKey)
  }

  keys() {
    /* get the ordered array of all stored keys
     */
    const rawKeys = Object.keys(localStorage)
      .filter(rawKey => rawKey.startsWith(this.keyPrefix))
      .map(rawKey => this.getUserKey(rawKey))
    rawKeys.sort()
    return rawKeys
  }
}


class LogProvider {
  /* Issues messages to the interface and/or console
   * Not used for debug messages
   */
  constructor() {
    this.place = $("#progress")
    this.clearProgress()
  }
  init() {
    this.placeProgress("Javascript has kicked in.")
  }
  later() {
  }
  async done() {
    this.placeProgress("Done ...")
    await new Promise(r => setTimeout(r, 1000))
    this.clearProgress()
  }

  clearProgress() {
    /* Clear progress messages in specified location
     * See placeProgress
     */
    this.place.html("")
  }
  placeProgress(msg) {
    /* Draw a progress message on the interface
     * The message is drawn in element box
     */
    this.place.append(`${msg}<br>`)
  }

  progress(msg) {
    /* issue a message to the console
     */
    console.log(msg)
  }

  clearError(box, ebox) {
    /* Clear error formatting in specified locations
     * See placeError
     */
    box.removeClass("error")
    ebox.html("")
    ebox.hide()
  }

  placeError(box, ebox, msg) {
    /* Draw an error on the interface
     * The error is drawn in element ebox,
     * and the element box receives error formatting
     */
    console.error(msg)
    box.addClass("error")
    ebox.show()
    ebox.html(msg)
  }

  error(msg) {
    /* issue a error message to the console
     * Use it for errors that we can recover from
     */
    console.error(msg)
  }
}

/* INFORMATIONAL MESSAGES
 *
 * Progress and debug messages
 */

const tell = msg => {
  /* issue a debug message to the console
   * Only if the DEBUG flag is true
   */
  if (DEBUG) {
    console.log("DEBUG", msg)
  }
}
tell("!!! IS ON !!!")


/* --- MAIN CHAPTER ----------------------------------------------
 */


class AppProvider {
/* TOP LEVEL ORCHESTRATION
 *
 * We take care to use an async function for the longish
 * initialization, so that we can display progress messages
 * in the mean time
 *
 * Document loading:
 * we take care that the user sees as much of the interface as early as possible.
 * We specifiy all scripts in the header of the document, but with the defer
 * attribute, so that the scripts load asynchronously
 * and are executed in the given order:
 *
 * configdata.js
 *  - information on the basis of which this app builds the interface
 *  - small file
 * layered.js
 *  - the app itself (this very script that you are reading now)
 * corpusdata.js
 *  - texts and mappings from textual positions to nodes
 *  - a big file, multi-megabyte
 *
 * When the document is ready, and the app has been loaded, the app will execute
 * initInterface() which builds the interface.
 *
 * In the meanwhile, corpusdata is still being fetched, while the interface is
 * probably already rendered.
 * When corpusdata is in, the app will execute initCorpus().
 *
 * Then the app continues by fetching the most recent known job, if any,
 * and executes its query
 *
 * Only then the app is ready to use, and the progress/waiting markers disappear.
 */

  constructor() {
    /* create all Provider objects
     */
    this.Log = new LogProvider()
    this.Disk = new DiskProvider()
    this.Mem = new MemProvider()

    this.State = new StateProvider()
    this.Job = new JobProvider()
    this.Gui = new GuiProvider()

    this.Config = new ConfigProvider()
    this.Corpus = new CorpusProvider()
    this.Search = new SearchProvider()

    /* let Provider objects register their dependencies on
     * other Provider objects
     */
    this.deps()
  }

  deps() {
    const { Mem, State, Job, Gui, Corpus, Search } = this

    Mem.deps(this)
    State.deps(this)
    Gui.deps(this)
    Job.deps(this)
    Corpus.deps(this)
    Search.deps(this)
  }

  init() {
    /* make all Provider objects ready,
     * except the ones that take time to load
     * (see later()
     */
    const { Log, Mem, State, Job, Gui, Config } = this

    Log.init()
    Config.init()
    Mem.init()

    State.init()
    Job.init()
    Gui.init()
  }

  async later() {
    /* continue work after the corpus data is in
     */
    const { Log, Job, Corpus } = this

    Log.later()
    Corpus.init()
    Job.later()
    Log.done()
  }
}

/* MAIN PROGRAM
 */

let A

$(() => {
  /* DOM is loaded, not all data has arrived
   */
  A = new AppProvider()
  A.init()
})

$(window).on("load", () => {
  // All data has arrived
  A.later()
})
