"""Ferramentas para o agente de análise de dados"""

import asyncio
import io
import uuid

import pandas as pd
import plotly.express as px
from langchain.tools import tool
from langchain_experimental.tools import PythonAstREPLTool
from plotly.basedatatypes import BaseFigure
from sklearn.cluster import KMeans

from src.services.data_processing_services import session_manager
from src.services.db_services import insert_graphs_db


def _save_graph_to_db(fig: BaseFigure, metadata: str) -> str:
    """
    Função para salvar o JSON gerado por ferramentas no banco de dados.
    """
    graph_id = str(uuid.uuid4())
    graph_json = fig.to_json()
    insert_graphs_db(graph_id, graph_json, metadata)

    return graph_id


async def _get_df(session_id: str):
    return await session_manager.get_df(session_id)


def _get_data_summary(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    info_buffer = io.StringIO()
    df.info(buf=info_buffer)
    info_str = info_buffer.getvalue()

    desc_str = df.describe(include='all').to_string()

    return f'Data Summary:\n\n{info_str}\n\nDescriptive Statistics:\n{desc_str}'


def _get_data_rows(
    df: pd.DataFrame, n_rows: int = 10, sample_method: str = 'head'
) -> str:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if not isinstance(n_rows, int) or n_rows <= 0:
        return 'Error: Number of rows (n_rows) must be a positive integer.'

    if sample_method == 'head':
        return df.head(n_rows).to_string()
    elif sample_method == 'tail':
        return df.tail(n_rows).to_string()
    elif sample_method == 'random':
        return df.sample(n=min(n_rows, len(df))).to_string()

    return "Error: Invalid sample_method. Choose from 'head', 'tail', or 'random'."


def _get_correlation_matrix(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    numeric_df = df.select_dtypes(include='number')

    if numeric_df.empty:
        return 'No numeric columns found to calculate correlation.'

    return numeric_df.corr().to_string()


def _detect_outliers_iqr(df: pd.DataFrame, column: str) -> str:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if column not in df.columns:
        return f'Error: Column "{column}" not found in the dataset.'

    if not pd.api.types.is_numeric_dtype(df[column]):
        return f'Error: Column "{column}" is not numeric.'

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]

    if outliers.empty:
        return f'No outliers detected in column "{column}".'

    return f'Detected {len(outliers)} outliers in column "{column}":\n{outliers.to_string()}'


def _create_histogram(df: pd.DataFrame, column: str) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if column not in df.columns:
        return f'Error: Column "{column}" not found in the dataset.'

    if not pd.api.types.is_numeric_dtype(df[column]):
        return f'Error: Column "{column}" is not numeric. Use create_bar_chart for categorical columns.'

    stats = df[column].describe()
    metadata = (
        f"Graph Type: Histogram for the '{column}' column. "
        f'Visualizes the frequency distribution of the column. '
        f'Key statistics: Mean={stats.get("mean", "N/A"):.2f}, '
        f'Median={stats.get("50%", "N/A"):.2f}, '
        f'Max={stats.get("max", "N/A"):.2f}, '
        f'Min={stats.get("min", "N/A"):.2f}. '
        f"The X-axis is '{column}' and the Y-axis is the count of occurrences."
    )

    fig = px.histogram(df, x=column)
    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': f'Histogram for "{column}" created successfully.',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _create_scatter_plot(df: pd.DataFrame, x_column: str, y_column: str) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if x_column not in df.columns or y_column not in df.columns:
        return 'Error: One or both columns not found in the dataset.'

    correlation_value = df[x_column].corr(df[y_column])

    abs_corr = abs(correlation_value)
    if abs_corr >= 0.7:
        strength = 'Strong Linear Relationship'
    elif abs_corr >= 0.3:
        strength = 'Moderate Linear Relationship'
    else:
        strength = 'Weak or No Linear Relationship'

    direction = (
        'Positive'
        if correlation_value > 0
        else ('Negative' if correlation_value < 0 else 'Neutral')
    )
    relationship_summary = f'{strength}, Direction: {direction}'

    metadata = (
        'chart_type: scatter_plot\n'
        'analysis_method: bivariate_relationship_analysis\n'
        f'x_variable: {x_column}\n'
        f'y_variable: {y_column}\n'
        f'correlation_coefficient: {round(correlation_value, 4)}\n'
        f'relationship_summary: {relationship_summary}\n'
        f'x_min_max: {round(df[x_column].min(), 2), round(df[x_column].max(), 2)}\n'
        f'y_min_max: {round(df[y_column].min(), 2), round(df[y_column].max(), 2)}\n'
        'agent_instruction: The agent must report the "relationship_summary" and the "correlation_coefficient" to the user to explain the pattern observed in the plot.'
    )

    fig = px.scatter(df, x=x_column, y=y_column)
    graph_id = _save_graph_to_db(fig, metadata)
    return {
        'response': f'Scatter plot for "{x_column}" vs "{y_column}" created successfully.',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _create_bar_chart(df: pd.DataFrame, column: str) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if column not in df.columns:
        return f'Error: Column "{column}" not found in the dataset.'

    if pd.api.types.is_numeric_dtype(df[column]):
        return f'Error: Column "{column}" is numeric. Use create_histogram for numeric columns.'

    counts = df[column].value_counts().reset_index()
    counts.columns = [column, 'count']
    fig = px.bar(counts, x=column, y='count', title=f'Distribution of {column}')

    metadata = (
        f"Graph Type: Bar Chart for the '{column}' column. "
        f'Visualizes the count of each category in the column. '
        f"The X-axis represents the categories of '{column}' and the Y-axis represents the frequency: \n{counts}."
    )

    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': f'Bar chart for "{column}" created successfully.',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _create_line_plot(df: pd.DataFrame, x_column: str, y_column: str) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if x_column not in df.columns or y_column not in df.columns:
        return 'Error: One or both columns not found in the dataset.'

    fig = px.line(
        df, x=x_column, y=y_column, title=f'Trend of {y_column} over {x_column}'
    )

    df_sorted = df.sort_values(by=x_column)

    start_value = df_sorted[y_column].iloc[0]
    end_value = df_sorted[y_column].iloc[-1]
    overall_change_percentage = (
        ((end_value - start_value) / start_value) * 100
        if start_value != 0
        else float('inf')
    )

    import numpy as np

    x_indices = np.arange(len(df_sorted))
    slope, _ = np.polyfit(x_indices, df_sorted[y_column], 1)

    if slope > 0.05 * np.mean(df_sorted[y_column]):
        trend_summary = 'Strongly Increasing'
    elif slope < -0.05 * np.mean(df_sorted[y_column]):
        trend_summary = 'Strongly Decreasing'
    else:
        trend_summary = 'Stable/Weak Trend'

    metadata = (
        'chart_type: line_plot_trend\n'
        'analysis_method: time_series_trend_analysis\n'
        f'x_variable: {x_column}\n'
        f'y_variable: {y_column}\n'
        f'start_value: {round(start_value, 2)}\n'
        f'end_value: {round(end_value, 2)}\n'
        f'overall_change_percentage: {round(overall_change_percentage, 2)}\n'
        f'trend_summary: {trend_summary}\n'
        'agent_instruction: Describe the overall direction based on "trend_summary" and quantify the total change using "overall_change_percentage".'
    )

    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': f'Line plot for "{y_column}" over "{x_column}" created successfully.',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _create_box_plot(df: pd.DataFrame, y_column: str, x_column: str = None) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if y_column not in df.columns:
        return f'Error: Column "{y_column}" not found in the dataset.'
    if not pd.api.types.is_numeric_dtype(df[y_column]):
        return f'Error: Column "{y_column}" must be numeric for a box plot.'

    stats = df[y_column].describe()
    metadata = (
        f"Graph Type: Box Plot for the '{y_column}' column.\n"
        f'Visualizes the distribution and identifies outliers.\n'
        f'Key statistics: Mean={stats.get("mean", "N/A"):.2f}, '
        f'Q1={stats.get("25%", "N/A"):.2f}, Median={stats.get("50%", "N/A"):.2f}, '
        f'Q3={stats.get("75%", "N/A"):.2f}, Max={stats.get("max", "N/A"):.2f}, '
        f'Min={stats.get("min", "N/A"):.2f}.'
    )

    title = f'Box Plot for {y_column}'
    if x_column:
        if x_column not in df.columns:
            return f'Error: Grouping column "{x_column}" not found in the dataset.'
        title += f' grouped by {x_column}'
        metadata += (
            f" Optionally grouped by the categorical column '{x_column}' on the X-axis."
        )

    fig = px.box(df, y=y_column, x=x_column, title=title)

    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': f'Box plot for "{y_column}" created successfully.',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _create_correlation_heatmap(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    numeric_df = df.select_dtypes(include='number')

    if numeric_df.shape[1] < 2:
        return 'Error: At least two numeric columns are required to create a correlation heatmap.'

    corr_matrix = numeric_df.corr()
    fig = px.imshow(corr_matrix, text_auto=True, title='Correlation Heatmap')

    corr_unstacked = corr_matrix.abs().unstack()
    corr_sorted = corr_unstacked.sort_values(kind='quicksort', ascending=False)
    unique_pairs = corr_sorted[corr_sorted < 1.0]
    unique_pairs = unique_pairs[~unique_pairs.index.duplicated()].head(5)

    top_correlations = []
    for (var1, var2), abs_corr in unique_pairs.items():
        original_corr = corr_matrix.loc[var1, var2]
        top_correlations.append(
            {
                'variable_1': var1,
                'variable_2': var2,
                'correlation_value': round(original_corr, 4),
                'strength': 'Strong'
                if abs_corr >= 0.7
                else ('Moderate' if abs_corr >= 0.3 else 'Weak'),
                'direction': 'Positive' if original_corr > 0 else 'Negative',
            }
        )

    metadata = (
        'chart_type: correlation_heatmap\n'
        'analysis_method: bivariate_correlation_analysis\n'
        'plot_purpose: Visualization of Linear Relationships between all Numeric Variables'
        'metric_calculated: Pearson Correlation Coefficient (r)\n'
        f'variable_scope: {numeric_df.columns.tolist()}\n'
        'interpretation_key: Values near +1 indicate strong positive correlation (ambas variáveis aumentam juntas); Values near -1 indicate strong negative correlation (uma variável aumenta, a outra diminui); Values near 0 indicate no linear relationship.'
        f'top_correlation_pairs: {top_correlations}\n'
        'agent_instruction: Describe the relationship between the strongest pairs listed in "top_correlation_pairs".'
    )
    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': 'Correlation heatmap created successfully.',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _find_clusters_and_plot(
    df: pd.DataFrame, x_column: str, y_column: str, n_clusters: int
) -> dict:
    if df is None or df.empty:
        return 'DataFrame empty, no data to analyse.'

    if x_column not in df.columns or y_column not in df.columns:
        return 'Error: One or both columns not found in the dataset.'

    if not pd.api.types.is_numeric_dtype(
        df[x_column]
    ) or not pd.api.types.is_numeric_dtype(df[y_column]):
        return f'Error: Columns "{x_column}" and "{y_column}" must be numeric for clustering.'

    if n_clusters <= 0:
        return f'Error: Non-positive clusters value received! n_clusters: {n_clusters}'

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_data = df[[x_column, y_column]].dropna()
    cluster_data['cluster'] = kmeans.fit_predict(cluster_data)
    cluster_data['cluster'] = cluster_data['cluster'].astype(str)

    cluster_summary = (
        cluster_data.groupby('cluster')[[x_column, y_column]]
        .agg(['mean', 'std', 'size'])
        .reset_index()
    )

    cluster_summary.columns = [
        f'{col[0]}_{col[1]}' if isinstance(col, tuple) else col
        for col in cluster_summary.columns
    ]

    size_col_name = f'{x_column}_size'
    cluster_summary.rename(columns={size_col_name: 'cluster_size'}, inplace=True)

    total_points = len(cluster_data)

    cluster_summary['cluster_percentage'] = (
        cluster_summary['cluster_size'] / total_points
    ) * 100

    fig = px.scatter(
        cluster_data,
        x=x_column,
        y=y_column,
        color='cluster',
        title=f'Clusters in {x_column} vs {y_column}',
    )

    metadata = (
        'chart_type: scatter_plot_with_clusters\n'
        'analysis_method: clustering_kmeans_result\n'
        f'plot_purpose: Visualização da Segmentação de Dados ({n_clusters} clusters) baseada em {x_column} e {y_column}\n'
        f'x_axis_variable: {x_column}\n'
        f'y_axis_variable: {y_column}\n'
        f'number_of_clusters: {n_clusters}\n'
        f'total_data_points: {total_points}\n'
        'interpretation_guide O agente deve usar as "Cluster Summaries" para descrever a localização, a característica central e a importância relativa (tamanho/porcentagem) de cada grupo no plano X-Y ao usuário.\n'
        f'cluster_summaries:\n {cluster_summary}'
    )

    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': f'Cluster plot for "{x_column}" vs "{y_column}" with {n_clusters} clusters created successfully. 📊',
        'graph_id': graph_id,
        'metadata': metadata,
    }


def _execute_python_code(df: pd.DataFrame, code: str):
    python_executor = PythonAstREPLTool(
        locals={
            '_save_graph_to_db': _save_graph_to_db,
            'pd': pd,
            'px': px,
            'df': df,
        }
    )

    return python_executor.run(code)


def get_analysis_tools(session_id: str) -> list:
    """
    Factory Method para criar e retornar uma lista de ferramentas do LangChain
    que injetam o session_id e chamam as funções originais.

    Args:
        session_id (str): Identificador da sessão atual.

    Returns:
        list (Tool): Lista de ferramentas do agente.
    """

    @tool('get_data_summary')
    async def get_data_summary() -> str:
        """
        Returns a string with a summary of the DataFrame, including dtypes,
        non-null counts, and descriptive statistics. Use this to get a general
        overview of the dataset.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_get_data_summary, df)

    @tool('get_data_rows')
    async def get_data_rows(n_rows: int = 10, sample_method: str = 'head') -> str:
        """
        Returns a sample of N rows from the DataFrame.
        Use this to get a quick sample of the data and see its structure.

        Args:
            n_rows (int): The number of rows to return, limited to 20 rows. Defaults to 10.
            sample_method (str): The method for sampling.
            Can be 'head' (first N rows), 'tail' (last N rows), or 'random' (N random rows). Defaults to 'head'.
        """

        if n_rows > 20:
            return {'error': 'n_rows exceeded the limit, please use a lower value!'}

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(
            _get_data_rows, df, n_rows=n_rows, sample_method=sample_method
        )

    @tool('get_correlation_matrix')
    async def get_correlation_matrix() -> str:
        """
        Returns the correlation matrix for the numeric columns of the DataFrame.
        Use this to understand the linear relationships between numeric variables.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_get_correlation_matrix, df)

    @tool('detect_outliers_iqr')
    async def detect_outliers_iqr(column: str) -> str:
        """
        Detects outliers in a numeric column using the IQR method.
        Use this to identify unusual data points in a specific column.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_detect_outliers_iqr, df, column)

    @tool('create_histogram')
    async def create_histogram(column: str) -> dict:
        """
        Generates a histogram for a given column, saves it, and returns its unique ID.
        Use this to visualize the distribution of a single numeric variable.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_create_histogram, df, column)

    @tool('create_scatter_plot')
    async def create_scatter_plot(x_column: str, y_column: str) -> dict:
        """
        Generates a scatter plot for two columns, saves it, and returns its unique ID.
        Use this to visualize the relationship between two numeric variables.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_create_scatter_plot, df, x_column, y_column)

    @tool('create_bar_chart')
    async def create_bar_chart(column: str) -> dict:
        """
        Generates a bar chart for a given categorical column, saves it, and returns its unique ID.
        Use this to visualize the frequency distribution of a categorical variable.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_create_bar_chart, df, column)

    @tool('create_line_plot')
    async def create_line_plot(x_column: str, y_column: str) -> dict:
        """
        Generates a line plot, saves it, and returns its unique ID.
        Use this to visualize trends over time. 'x_column' should ideally be a datetime column.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_create_line_plot, df, x_column, y_column)

    @tool('create_box_plot')
    async def create_box_plot(y_column: str, x_column: str = None) -> dict:
        """
        Generates a box plot, saves it, and returns its unique ID.
        Use this to visualize the distribution of a numeric variable (y_column),
        optionally grouped by a categorical variable (x_column).
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_create_box_plot, df, y_column, x_column)

    @tool('create_correlation_heatmap')
    async def create_correlation_heatmap() -> dict:
        """
        Generates a correlation heatmap for numeric columns, saves it, and returns its ID.
        Use this for a visual overview of the linear relationships between variables.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(_create_correlation_heatmap, df)

    @tool('find_clusters_and_plot')
    async def find_clusters_and_plot(
        x_column: str, y_column: str, n_clusters: int
    ) -> dict:
        """
        Performs K-Means clustering and generates a scatter plot, saves it, and returns its unique ID.
        Use this to identify and visualize groupings in your data.
        """

        df: pd.DataFrame = await _get_df(session_id)
        return await asyncio.to_thread(
            _find_clusters_and_plot, df, x_column, y_column, n_clusters
        )

    @tool('execute_python_code')
    async def execute_python_code(code: str):
        """Executes Python code in a secure environment. Use this tool for complex tasks requiring data processing, statistics, or custom DataFrame manipulation, such as filtering, grouping, complex calculations, or graph generation.
        You have access to the following.
            pd: Pandas.
            px: Plotly Express.
            df: the current dataframe to analyse
            _save_graph_to_db(fig, metadata): saves a Plotly figure.
        Mandatory Execution Steps:
        LOAD DATA: check if is data available:
        if df is None or df.empty:
            # Stop execution if data is missing
            ...
        * CALCULATIONS: For analysis, use print() to return results. Keep the output small and concise for efficiency; avoid printing large DataFrames.
        * Graph Generation Protocol:
        To create a graph, follow these steps:
            * Generate Figure.
            * Generate Metadata: create a concise, textual summary of the graph (include stats from dataframe if possible for better understanding, be efficient in the data returned).
            * Save Figure: Call the required saving function and print metadata for analysis:
            print(_save_graph_to_db(fig, metadata), metadata)
        The function's output (graph_id, metadata) will be returned to you.
        """

        df = await session_manager.get_df(session_id)

        return await asyncio.to_thread(_execute_python_code, df, code)

    return [
        get_data_summary,
        get_data_rows,
        get_correlation_matrix,
        detect_outliers_iqr,
        create_histogram,
        create_scatter_plot,
        create_bar_chart,
        create_line_plot,
        create_box_plot,
        create_correlation_heatmap,
        find_clusters_and_plot,
        execute_python_code,
    ]
