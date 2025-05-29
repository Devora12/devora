import { useState, useEffect } from 'react';
import { projectsApi, handleApiError } from '../services/api';

export const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const response = await projectsApi.getAll();
        setProjects(response.data);
        setError(null);
      } catch (err) {
        const errorMessage = handleApiError(err, 'Fetch Projects');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  return { projects, loading, error };
};

export const useProjectData = (projectId) => {
  const [testcasesByAuthor, setTestcasesByAuthor] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!projectId) return;

    const fetchProjectData = async () => {
      try {
        setLoading(true);
        const [testcasesResponse, authorsResponse] = await Promise.all([
          projectsApi.getTestcasesByAuthor(projectId),
          projectsApi.getAuthors(projectId)
        ]);
        
        setTestcasesByAuthor(testcasesResponse.data);
        setAuthors(authorsResponse.data);
        setError(null);
      } catch (err) {
        const errorMessage = handleApiError(err, 'Fetch Project Data');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchProjectData();
  }, [projectId]);

  return { testcasesByAuthor, authors, loading, error };
};