# AN-ROB-2020 (pre-registered robustness, addendum Section 4)

Aggregate variants: DT-GSK's ordinal is stable (no instability disclosure triggered).

verdict: **diverge**

divergences:
- mean_vs_median@5:agsk ordinal 2->1
- mean_vs_median@5:apgsk ordinal 1->2
- mean_vs_median@5:fdb-agsk ordinal 2->3
- mean_vs_median@5:wtl vs gsk (4, 1, 3)->(3, 5, 0)
- mean_vs_median@5:wtl vs agsk (2, 1, 5)->(1, 3, 4)
- mean_vs_median@5:wtl vs apgsk (1, 1, 6)->(1, 3, 4)
- mean_vs_median@5:wtl vs fdb-agsk (2, 1, 5)->(2, 3, 3)
- mean_vs_median@5:wtl vs atmals-gsk (5, 1, 2)->(4, 4, 0)
- mean_vs_median@5:wtl vs egsk (5, 1, 2)->(3, 5, 0)
- mean_vs_median@10:agsk ordinal 1->2
- mean_vs_median@10:fdb-agsk ordinal 2->1
- mean_vs_median@10:wtl vs gsk (8, 1, 1)->(6, 3, 1)
- mean_vs_median@10:wtl vs agsk (1, 1, 8)->(2, 2, 6)
- mean_vs_median@10:wtl vs apgsk (2, 1, 7)->(2, 2, 6)
- mean_vs_median@10:wtl vs atmals-gsk (6, 1, 3)->(4, 4, 2)
- mean_vs_median@10:wtl vs egsk (8, 1, 1)->(7, 3, 0)
- mean_vs_median@15:gsk ordinal 5->6
- mean_vs_median@15:apgsk ordinal 3->4
- mean_vs_median@15:fdb-agsk ordinal 2->3
- mean_vs_median@15:dt-gsk ordinal 3->2
- mean_vs_median@15:wtl vs gsk (7, 2, 1)->(7, 3, 0)
- mean_vs_median@15:wtl vs agsk (2, 2, 6)->(2, 4, 4)
- mean_vs_median@15:wtl vs apgsk (2, 2, 6)->(4, 3, 3)
- mean_vs_median@15:wtl vs fdb-agsk (2, 2, 6)->(4, 3, 3)
- mean_vs_median@15:wtl vs atmals-gsk (8, 2, 0)->(7, 3, 0)
- mean_vs_median@15:wtl vs egsk (8, 2, 0)->(7, 3, 0)
- mean_vs_median@20:atmals-gsk ordinal 6->7
- mean_vs_median@20:egsk ordinal 7->6
- mean_vs_median@20:wtl vs gsk (4, 1, 5)->(3, 1, 6)
- mean_vs_median@20:wtl vs agsk (0, 1, 9)->(1, 2, 7)
- mean_vs_median@20:wtl vs apgsk (2, 1, 7)->(2, 2, 6)
- mean_vs_median@20:wtl vs fdb-agsk (0, 1, 9)->(1, 2, 7)
- mean_vs_median@20:wtl vs egsk (8, 1, 1)->(5, 1, 4)
- aggregate_D10_15_20_only:gsk ordinal 6->5
- aggregate_D10_15_20_only:atmals-gsk ordinal 7->6
- aggregate_D10_15_20_only:egsk ordinal 5->7
