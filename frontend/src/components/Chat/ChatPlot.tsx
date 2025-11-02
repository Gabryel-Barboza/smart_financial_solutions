import Plot from 'react-plotly.js';

import axios from 'axios';
import { FaSpinner } from 'react-icons/fa6';
import { useEffect, useState } from 'react';

import { useServerContext } from '../../context/serverContext/useServerContext';
import type { PlotlyFigure, ResponseGraphSchema } from '../../schemas/InputSchema';
import { useToastContext } from '../../context/toastContext/useToastContext';

interface Props {
  graphId: string;
}

function ChatPlot({ graphId }: Props) {
  const { addToast } = useToastContext();
  const { API_URL } = useServerContext();
  const [isLoading, setIsLoading] = useState(true);
  const [figure, setFigure] = useState<PlotlyFigure | null>(null);

  useEffect(() => {
    async function fetchGraph() {
      const url = API_URL + `/graphs/${graphId}`;
      try {
        const response = await axios.get(url);

        const content = response.data as ResponseGraphSchema;
        const graphJson: PlotlyFigure = JSON.parse(content.graph);

        setFigure(graphJson);
      } catch (err) {
        console.log(err);

        if (axios.isAxiosError(err)) addToast(`${err.response}`, 'error');
        else if (err instanceof Error) addToast(err.message, 'error');
      } finally {
        setIsLoading(false);
      }
    }

    fetchGraph();
  }, [API_URL, graphId, addToast]);

  return (
    <>
      {isLoading && (
        <div className="text-4xl text-blue-600 ml-8 mb-4 w-fit animate-spin">
          <FaSpinner />
        </div>
      )}
      {figure && <Plot data={figure.data} layout={figure.layout} />}
    </>
  );
}

export default ChatPlot;
