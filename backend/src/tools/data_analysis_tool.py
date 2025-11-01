"""Ferramentas para o agente de análise de dados"""

import asyncio
import io
import uuid

import pandas as pd
import plotly.express as px
from langchain.tools import tool
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

    metadata = (
        f"Graph Type: Scatter Plot between '{x_column}' and '{y_column}'. "
        f'Visualizes the relationship between the two variables. '
        f"The X-axis represents '{x_column}' and the Y-axis represents '{y_column}'. "
        f'Each point corresponds to an observation in the data.'
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

    metadata = (
        f"Graph Type: Bar Chart for the '{column}' column. "
        f'Visualizes the count of each category in the column. '
        f"The X-axis represents the categories of '{column}' and the Y-axis represents the frequency (count)."
    )

    counts = df[column].value_counts().reset_index()
    counts.columns = [column, 'count']
    fig = px.bar(counts, x=column, y='count', title=f'Distribution of {column}')

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

    metadata = (
        f"Graph Type: Line Plot of '{y_column}' over '{x_column}'. "
        f"Visualizes the trend of the '{y_column}' variable along '{x_column}'. "
        f'Ideal for visualizing data over time.'
    )

    fig = px.line(
        df, x=x_column, y=y_column, title=f'Trend of {y_column} over {x_column}'
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
        f"Graph Type: Box Plot for the '{y_column}' column. "
        f'Visualizes the distribution and identifies outliers. '
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

    metadata = 'Graph Type: Correlation Heatmap. Visualizes the correlation matrix for the numeric columns of the dataset. The colors indicate the strength and direction of the linear correlation between pairs of variables.'

    corr_matrix = numeric_df.corr()
    fig = px.imshow(corr_matrix, text_auto=True, title='Correlation Heatmap')
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

    metadata = f"Graph Type: Scatter Plot with Clusters. Runs the K-Means algorithm to find {n_clusters} clusters in the data based on the '{x_column}' and '{y_column}' columns. The colors represent the identified clusters."

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_data = df[[x_column, y_column]].dropna()
    cluster_data['cluster'] = kmeans.fit_predict(cluster_data)
    cluster_data['cluster'] = cluster_data['cluster'].astype(str)

    fig = px.scatter(
        cluster_data,
        x=x_column,
        y=y_column,
        color='cluster',
        title=f'Clusters in {x_column} vs {y_column}',
    )
    graph_id = _save_graph_to_db(fig, metadata)

    return {
        'response': f'Cluster plot for "{x_column}" vs "{y_column}" with {n_clusters} clusters created successfully. 📊',
        'graph_id': graph_id,
        'metadata': metadata,
    }


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
            n_rows (int): The number of rows to return. Defaults to 10.
            sample_method (str): The method for sampling.
            Can be 'head' (first N rows), 'tail' (last N rows), or 'random' (N random rows). Defaults to 'head'.
        """

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
    ]
