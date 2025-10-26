import Plot from 'react-plotly.js';

import axios, { HttpStatusCode } from 'axios';
import { FaSpinner } from 'react-icons/fa6';
import { useEffect, useState } from 'react';

import type { Data, Layout } from 'plotly.js';

import { useServerContext } from '../../context/serverContext/useServerContext';

interface PlotlyFigure {
  data: Data[];
  layout: Partial<Layout>;
}

interface Props {
  graphId: string;
}

function ChatPlot({ graphId }: Props) {
  const { API_URL } = useServerContext();
  const [isLoading, setIsLoading] = useState(true);
  const [figure, setFigure] = useState<PlotlyFigure | null>(null);

  useEffect(() => {
    async function fetchGraph() {
      const url = API_URL + `/graphs/${graphId}`;
      try {
        const response = await axios.get(url);

        if (response.status !== HttpStatusCode.Ok) {
          console.log(`Failed to fetch graph with id ${graphId}`);
          return;
        }

        const graphJson = response.data.graph;
        setFigure(graphJson);
      } catch (err) {
        console.log(`Failed to fetch graph. Err: \n${err}`);
      } finally {
        setIsLoading(false);
      }
    }

    fetchGraph();
  }, [API_URL, graphId]);

  return (
    <>
      {isLoading && (
        <div className="text-4xl text-blue-600 ml-8 mb-4 w-fit animate-spin">
          <FaSpinner />
        </div>
      )}
      {figure && <Plot data={figure?.data} layout={figure?.layout} />}
    </>
  );
}

export default ChatPlot;
