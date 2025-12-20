import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Sparkles, RotateCcw, FileText, Brain, Trophy, CheckCircle2 } from 'lucide-react';
import api, { analyzeResumes } from '../services/api';
import RoleInput from '../components/RoleInput';
import WeightConfig from '../components/WeightConfig';
import { ThresholdConfig, DEFAULT_THRESHOLDS } from '../components/ThresholdConfig';
import DropZone from '../components/DropZone';
import FileList from '../components/FileList';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';

// Analysis progress steps
const ANALYSIS_STEPS = [
  { id: 'upload', label: 'Uploading', icon: FileText },
  { id: 'extract', label: 'Extracting', icon: FileText },
  { id: 'analyze', label: 'Analyzing', icon: Brain },
  { id: 'rank', label: 'Ranking', icon: Trophy },
];

function ProgressSteps({ currentStep }) {
  const stepIndex = ANALYSIS_STEPS.findIndex(s => s.id === currentStep);

  return (
    <div className="flex items-center justify-center gap-2 py-4">
      {ANALYSIS_STEPS.map((step, index) => {
        const Icon = step.icon;
        const isActive = index === stepIndex;
        const isComplete = index < stepIndex;

        return (
          <div key={step.id} className="flex items-center">
            <div className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm transition-all ${
              isActive
                ? 'bg-primary text-primary-foreground'
                : isComplete
                ? 'bg-primary/20 text-primary'
                : 'bg-muted text-muted-foreground'
            }`}>
              {isComplete ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : isActive ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Icon className="h-4 w-4" />
              )}
              <span className="hidden sm:inline">{step.label}</span>
            </div>
            {index < ANALYSIS_STEPS.length - 1 && (
              <div className={`w-4 h-0.5 mx-1 ${
                index < stepIndex ? 'bg-primary' : 'bg-muted'
              }`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

function HomePage() {
  const navigate = useNavigate();
  const [roles, setRoles] = useState([]);
  const [formData, setFormData] = useState({
    roleTitle: '',
    roleId: null,
    isNewRole: true,
  });
  const [jobDescription, setJobDescription] = useState('');
  const [weights, setWeights] = useState({
    experience: 20,
    projects: 20,
    positions: 20,
    skills: 20,
    education: 20,
  });
  const [files, setFiles] = useState([]);
  const [thresholds, setThresholds] = useState(DEFAULT_THRESHOLDS);
  const [errors, setErrors] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(null);

  const handleFilesAdded = (newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
    if (errors.files) {
      setErrors((prev) => ({ ...prev, files: '' }));
    }
  };

  const handleRemoveFile = (indexToRemove) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const response = await api.get('/roles');
        if (response.data.success) {
          setRoles(response.data.data.roles);
        }
      } catch (error) {
        console.warn('Failed to fetch roles:', error.message);
      }
    };
    fetchRoles();
  }, []);

  const handleRoleChange = (title) => {
    setFormData((prev) => ({
      ...prev,
      roleTitle: title,
    }));
    if (errors.roleTitle) {
      setErrors((prev) => ({ ...prev, roleTitle: '' }));
    }
  };

  const handleSelectExisting = (role) => {
    if (role) {
      setFormData((prev) => ({
        ...prev,
        roleId: role.id,
        isNewRole: false,
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        roleId: null,
        isNewRole: true,
      }));
    }
  };

  const handleJobDescriptionChange = (e) => {
    setJobDescription(e.target.value);
    if (errors.jobDescription) {
      setErrors((prev) => ({ ...prev, jobDescription: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.roleTitle.trim()) {
      newErrors.roleTitle = 'Role title is required';
    }

    if (!jobDescription.trim()) {
      newErrors.jobDescription = 'Job description is required';
    }

    if (files.length === 0) {
      newErrors.files = 'At least one resume is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const clearForm = () => {
    setFormData({ roleTitle: '', roleId: null, isNewRole: true });
    setJobDescription('');
    setWeights({ experience: 20, projects: 20, positions: 20, skills: 20, education: 20 });
    setThresholds(DEFAULT_THRESHOLDS);
    setFiles([]);
    setErrors({});
    toast({
      title: 'Form cleared',
      description: 'All fields have been reset.',
    });
  };

  const handleAnalyze = async () => {
    if (!validateForm()) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields.',
        variant: 'destructive',
      });
      return;
    }

    setIsAnalyzing(true);
    setErrors({});
    setAnalysisStep('upload');

    try {
      // Build FormData for multipart upload
      const submitData = new FormData();
      submitData.append('role_title', formData.roleTitle.trim());
      submitData.append('job_description', jobDescription.trim());
      submitData.append('weights', JSON.stringify(weights));
      submitData.append('thresholds', JSON.stringify(thresholds));

      // Add all files
      files.forEach((file) => {
        submitData.append('files', file);
      });

      // Simulate progress steps (the actual API does all steps at once)
      setAnalysisStep('extract');
      await new Promise(r => setTimeout(r, 500));
      setAnalysisStep('analyze');
      await new Promise(r => setTimeout(r, 500));
      setAnalysisStep('rank');

      const response = await analyzeResumes(submitData);

      if (response.success) {
        toast({
          title: 'Analysis Complete!',
          description: `Successfully analyzed ${files.length} resume${files.length !== 1 ? 's' : ''}.`,
        });
        // Navigate to dashboard with session ID
        navigate(`/dashboard/${response.data.session_id}`);
      } else {
        throw new Error(response.error?.message || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      const errorMessage = error.response?.data?.error?.message || error.message || 'Failed to analyze resumes';
      setErrors({ submit: errorMessage });
      toast({
        title: 'Analysis Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsAnalyzing(false);
      setAnalysisStep(null);
    }
  };

  const isFormValid = formData.roleTitle.trim() && jobDescription.trim() && files.length > 0;
  const hasAnyInput = formData.roleTitle || jobDescription || files.length > 0;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-3">
          <Sparkles className="h-10 w-10 text-primary" />
          <h1 className="text-5xl text-foreground">TalentLens AI</h1>
        </div>
        <p className="text-xl text-muted-foreground">
          AI-powered resume shortlisting and candidate ranking
        </p>
      </div>

      {/* Main Form Card */}
      <Card className="border-border shadow-lg">
        <CardContent className="p-6 sm:p-8 space-y-8">
          {/* Role Title */}
          <div className="space-y-3">
            <label className="text-base font-semibold text-foreground">Role Title</label>
            <RoleInput
              roles={roles}
              value={formData.roleTitle}
              onChange={handleRoleChange}
              onSelectExisting={handleSelectExisting}
            />
            {formData.roleTitle && (
              <p className="text-sm text-muted-foreground">
                {formData.isNewRole
                  ? 'New role will be created'
                  : `Adding to existing role pool`}
              </p>
            )}
            {errors.roleTitle && (
              <p className="text-sm text-destructive">{errors.roleTitle}</p>
            )}
          </div>

          {/* Job Description */}
          <div className="space-y-3">
            <label className="text-base font-semibold text-foreground">Job Description</label>
            <p className="text-sm text-muted-foreground">
              Paste the full job description to help AI understand role requirements
            </p>
            <Textarea
              placeholder="Paste the full job description here...

Include requirements like:
• Years of experience needed
• Required skills and technologies
• Educational requirements
• Key responsibilities"
              value={jobDescription}
              onChange={handleJobDescriptionChange}
              className="min-h-[180px] text-base bg-background border-border resize-none"
            />
            {errors.jobDescription && (
              <p className="text-sm text-destructive">{errors.jobDescription}</p>
            )}
          </div>

          {/* Weight Configuration */}
          <div className="space-y-3">
            <label className="text-base font-semibold text-foreground">Scoring Weights</label>
            <p className="text-sm text-muted-foreground">
              Adjust how much each dimension contributes to the final score
            </p>
            <WeightConfig weights={weights} onChange={setWeights} />
          </div>

          {/* Threshold Configuration */}
          <div className="space-y-3">
            <label className="text-base font-semibold text-foreground">Minimum Thresholds</label>
            <p className="text-sm text-muted-foreground">
              Set minimum scores to eliminate candidates who don&apos;t meet requirements
            </p>
            <ThresholdConfig thresholds={thresholds} onChange={setThresholds} />
          </div>

          {/* Resume Upload */}
          <div className="space-y-3">
            <label className="text-base font-semibold text-foreground">
              Upload Resumes
            </label>
            <p className="text-sm text-muted-foreground">
              Upload PDF resumes to analyze ({files.length} selected)
            </p>
            <DropZone onFilesAdded={handleFilesAdded} />
            <FileList files={files} onRemove={handleRemoveFile} />
            {errors.files && (
              <p className="text-sm text-destructive">{errors.files}</p>
            )}
          </div>

          {/* Submit Error */}
          {errors.submit && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
              <p className="text-sm text-destructive">{errors.submit}</p>
            </div>
          )}

          {/* Progress Steps (shown during analysis) */}
          {isAnalyzing && analysisStep && (
            <ProgressSteps currentStep={analysisStep} />
          )}

          {/* Action Buttons */}
          <div className="pt-2 space-y-3">
            <Button
              onClick={handleAnalyze}
              disabled={!isFormValid || isAnalyzing}
              className="w-full h-14 text-lg font-semibold"
              size="lg"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing {files.length} Resume{files.length !== 1 ? 's' : ''}...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Analyze {files.length > 0 ? `${files.length} Resume${files.length !== 1 ? 's' : ''}` : 'Resumes'}
                </>
              )}
            </Button>

            {/* Clear Form Button */}
            {hasAnyInput && !isAnalyzing && (
              <Button
                variant="outline"
                onClick={clearForm}
                className="w-full"
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Clear Form
              </Button>
            )}

            {!isFormValid && !isAnalyzing && (
              <p className="text-center text-sm text-muted-foreground">
                {!formData.roleTitle.trim() && 'Enter a role title'}
                {formData.roleTitle.trim() && !jobDescription.trim() && 'Add a job description'}
                {formData.roleTitle.trim() && jobDescription.trim() && files.length === 0 && 'Upload at least one resume'}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default HomePage;
