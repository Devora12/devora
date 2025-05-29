import { useState, useEffect } from 'react';
import { authorsApi, handleApiError } from '../services/api';

export const useAuthorData = (author) => {
  const [authorTestcases, setAuthorTestcases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!author) return;

    const fetchAuthorTestcases = async () => {
      try {
        setLoading(true);
        const response = await authorsApi.getTestcases(author);
        setAuthorTestcases(response.data);
        setError(null);
      } catch (err) {
        const errorMessage = handleApiError(err, 'Fetch Author Testcases');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchAuthorTestcases();
  }, [author]);

  return { authorTestcases, loading, error };
};

export const useAuthorMetrics = (author, testcase = 'all') => {
  const [authorMetrics, setAuthorMetrics] = useState(null);
  const [workMetrics, setWorkMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!author) return;

    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const metricsTestcase = testcase === 'all' ? null : testcase;
        
        const [metricsResponse, workMetricsResponse] = await Promise.all([
          authorsApi.getMetrics(author, metricsTestcase),
          authorsApi.getWorkMetrics(author)
        ]);
        
        setAuthorMetrics(metricsResponse.data);
        setWorkMetrics(workMetricsResponse.data);
        setError(null);
      } catch (err) {
        const errorMessage = handleApiError(err, 'Fetch Author Metrics');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [author, testcase]);

  return { authorMetrics, workMetrics, loading, error };
};