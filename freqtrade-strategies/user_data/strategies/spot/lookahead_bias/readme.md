警告：此文件夹中的策略确实存在前视偏差。

请将这些策略视为练习示例，尝试找出其中的前视偏差。


<details>
<summary>展开查看提示／答案</summary>

请点击各个策略，查看具体错误。

<details>
<summary>DevilStra</summary>

`normalize()` 使用了 `.min()` 和 `.max()`。这会读取完整的数据帧，而不只是过去的数据。

</details>

<details>
<summary>GodStraNew</summary>

`normalize()` 使用了 `.min()` 和 `.max()`。这会读取完整的数据帧，而不只是过去的数据。
</details>
<details>
<summary>Zeus</summary>

使用 `.min()` 和 `.max()` 对 `trend_ichimoku_base` 与 `trend_kst_diff` 进行归一化。

</details>

<details>
<summary>wtc</summary>

``` python
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
```

使用 `MinMaxScaler` 会自动读取整个序列的绝对最大值和最小值。

</details>
</details>

</details>
