# Flowcharts And Diagrams

> **What this page is.** A visual map of the project — the same flows described
> in [Architecture](architecture.md) and [Workflows](workflows.md), drawn as
> flowcharts.
> **Who it is for.** Anyone who wants the shape of the system at a glance.
> **Prerequisites.** None; terms are defined in [the glossary](glossary.md).

The diagrams render in the HTML site. Each node uses an `id["label"]`
declaration so the flowcharts parse cleanly under Mermaid.

## Full Project Architecture

```mermaid
flowchart LR
  cli["CLI / Python API"] --> cfg["ExperimentConfig"]
  cfg --> seed["Seed Policy"]
  cfg --> fac["Benchmark Factory"]
  fac --> prob["BenchmarkProblem"]
  seed --> fair["Fair Start"]
  prob --> opt["Optimizer Kernel"]
  fair --> opt
  opt --> res["OptimizerResult"]
  res --> wr["Output Writers"]
  wr --> gen["Generated Results"]
  gen --> ver["Verification"]
  ref["Reference Tables"] --> ver
```

## Algorithm Execution Flow

```mermaid
flowchart TD
  s["Start optimizer"] --> rd["Read seed and options"]
  rd --> init["Initialize or accept fair-start population"]
  init --> ev["Evaluate initial fitness"]
  ev --> best["Record best-so-far"]
  best --> don["Generate junior/senior donor candidates"]
  don --> rep["Repair bounds"]
  rep --> evt["Evaluate trial population"]
  evt --> sel["Greedy or variant-specific selection"]
  sel --> upd["Update adaptive state"]
  upd --> budget{"Budget reached?"}
  budget -- "No" --> don
  budget -- "Yes" --> ret["Return OptimizerResult"]
```

## Benchmark Evaluation Pipeline

```mermaid
flowchart LR
  pop["Optimizer population matrix"] --> asp["as_population validation"]
  asp --> sev["Suite evaluator"]
  sev --> asf["as_fitness_vector validation"]
  asf --> fit["Fitness vector"]
```

## Experiment Lifecycle

```mermaid
flowchart TD
  ld["Load YAML or CLI args"] --> norm["Normalize ExperimentConfig"]
  norm --> cells["Resolve cells"]
  cells --> sched["Build seed schedule"]
  sched --> disp["Dispatch run tasks"]
  disp --> pr["Write per_run.csv"]
  pr --> sm["Write summaries and traces"]
  sm --> envp["Write environment/profile"]
  envp --> vj["Write verification.json"]
```

## Configuration Loading

```mermaid
flowchart LR
  ym["YAML mapping"] --> kk["Known key check"]
  cm["Direct CLI mapping"] --> kk
  kk --> sn["Suite normalization"]
  sn --> fn["Function normalization"]
  fn --> dn["Dimension normalization"]
  dn --> on["Optimizer normalization"]
  on --> cfg["ExperimentConfig"]
```

## Seed Generation And RNG Flow

```mermaid
flowchart TD
  base["Base seed"] --> pol["Seed policy (unified/reference/native/derived)"]
  pol --> rs["Run seed (get_cec_seed for unified)"]
  rs --> fam["GSK family path"]
  rs --> dt["DT-GSK path (UNIFIED_ONLY)"]
  fam --> rc["RandomContext (single stream)"]
  rc --> fair["Fair-start population"]
  fair --> post["Post-initialization RNG state"]
  post --> restore["Optimizer RNG restore"]
  restore --> draws["Algorithm random draws"]
  dt --> streams["RNGStreams: 13 named substreams (init = run seed verbatim)"]
  streams --> selfinit["Self-init 5*D population (fair-start exception)"]
  selfinit --> dtdraws["DT-GSK substream draws"]
```

## Parallel Execution Flow

```mermaid
flowchart LR
  cells["Resolved run cells"] --> sched["Seed schedule built serially"]
  sched --> tasks["RunTask list"]
  tasks --> pool["ProcessPoolExecutor (spawn)"]
  pool --> out["Task outcomes"]
  pool -- "worker crash" --> fb["Rebuild pool, else serial fallback"]
  fb --> out
  out --> order["Original order restoration"]
  order --> wr["Deterministic output writers"]
```

## Logging And Reporting Pipeline

```mermaid
flowchart TD
  res["OptimizerResult"] --> rr["RunRecord"]
  rr --> pr["per_run.csv"]
  res --> st["summary tables"]
  res --> cu["curves"]
  res --> cl["checkpoint logs"]
  cfg["ExperimentConfig"] --> envj["environment.json"]
  prof["Profile data"] --> pj["profile.json"]
  gs["Generated summaries"] --> vj["verification.json"]
```

## Optimizer Update Cycle

```mermaid
flowchart TD
  pop["Population"] --> rank["Rank by fitness"]
  rank --> jd["Junior donors"]
  rank --> sd["Senior donors"]
  jd --> jg["Junior gained vector"]
  sd --> sg["Senior gained vector"]
  jg --> tv["Trial vector"]
  sg --> tv
  tv --> rep["Bounds repair"]
  rep --> cmp["Fitness comparison"]
  cmp --> updt["Population update"]
```

## Validation Workflow

```mermaid
flowchart LR
  gcsv["Generated summary CSV"] --> lg["Load generated table"]
  rroot["Reference root"] --> fm["Find matching reference"]
  fm --> lr["Load reference table"]
  lg --> cmp["Compare statistics"]
  lr --> cmp
  cmp --> verdict["CONSISTENT or DEVIATES"]
  verdict --> vj["verification.json"]
```

## Statistical Analysis Flow

```mermaid
flowchart TD
  refs["Reference panel means (benchmarks/cec_reference_results, loaded first)"] --> load["result_loader"]
  prop["Fallback: reproduced means (results/_run_all)"] --> load
  load --> panel["7-algorithm family panel"]
  panel --> fried["Friedman ranks"]
  panel --> wil["Pairwise Wilcoxon + Holm"]
  panel --> eff["Vargha-Delaney A12 / win-tie-loss / BCa"]
  fried --> cd["Nemenyi CD + rank PNGs"]
  wil --> tex["LaTeX tables"]
  eff --> tex
  cd --> outp["results/_run_all/_analysis/&lt;suite&gt;"]
  tex --> outp
```

## Paper Review-Pack Flow

```mermaid
flowchart LR
  ck["CheckpointErrors_&lt;alg&gt;_F&lt;func&gt;_D&lt;dim&gt;.csv"] --> grid["7-algorithm convergence grids"]
  grid --> pdf["PdfPages render"]
  pdf --> out["papers/DT-GSK-CEC2017-review.pdf"]
  grid -- "absent curve" --> miss["papers/DT-GSK-CEC2017-review_missing.log"]
```

## Testing Workflow

```mermaid
flowchart LR
  u["Unit tests"] --> sm["Smoke tests"]
  sm --> r["Regression tests"]
  r --> p["Performance tests"]
  p --> d["Documentation tests"]
  d --> gate["Full pytest gate"]
```

## Performance Optimization Workflow

```mermaid
flowchart TD
  base["Baseline run"] --> prof["Profile"]
  prof --> bn["Identify bottleneck"]
  bn --> vj["Vectorize or JIT"]
  vj --> rerun["Re-run deterministic tests"]
  rerun --> cmp["Compare runtime"]
  cmp --> rec["Record performance report"]
```
