import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from '@docusaurus/router';
import { translate } from '@docusaurus/Translate';

const TranslationControls = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [personalizationEnabled, setPersonalizationEnabled] = useState(false);
  const [readingLevel, setReadingLevel] = useState('intermediate');
  const [learningStyle, setLearningStyle] = useState('visual');
  const [showOptions, setShowOptions] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  // Available languages for translation
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ur', name: 'Urdu' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' }
  ];

  // Reading levels for personalization
  const readingLevels = [
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  // Learning styles for personalization
  const learningStyles = [
    { value: 'visual', label: 'Visual' },
    { value: 'auditory', label: 'Auditory' },
    { value: 'reading', label: 'Reading/Writing' },
    { value: 'kinesthetic', label: 'Kinesthetic' }
  ];

  // Get current session ID from localStorage or create new one
  const getSessionId = () => {
    let sessionId = localStorage.getItem('textbook-session-id');
    if (!sessionId) {
      sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('textbook-session-id', sessionId);
    }
    return sessionId;
  };

  // Apply translation and personalization settings
  const applySettings = () => {
    const sessionId = getSessionId();

    // Update URL with query parameters for translation and personalization
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('language', selectedLanguage);
    searchParams.set('personalization', personalizationEnabled);
    searchParams.set('readingLevel', readingLevel);
    searchParams.set('learningStyle', learningStyle);
    searchParams.set('sessionId', sessionId);

    // Store preferences in localStorage
    const preferences = {
      language: selectedLanguage,
      reading_level: readingLevel,
      learning_style: learningStyle,
      personalization_enabled: personalizationEnabled
    };
    localStorage.setItem('user-preferences', JSON.stringify(preferences));

    // Navigate to updated URL
    navigate({
      pathname: location.pathname,
      search: searchParams.toString()
    }, { replace: true });

    // Trigger a page reload to apply the new settings
    window.location.reload();
  };

  // Reset to default settings
  const resetSettings = () => {
    setSelectedLanguage('en');
    setPersonalizationEnabled(false);
    setReadingLevel('intermediate');
    setLearningStyle('visual');

    // Clear preferences from localStorage
    localStorage.removeItem('user-preferences');

    // Update URL to remove query parameters
    navigate({
      pathname: location.pathname,
      search: ''
    }, { replace: true });

    // Trigger a page reload to apply default settings
    window.location.reload();
  };

  // Load saved preferences on component mount
  useEffect(() => {
    const savedPreferences = localStorage.getItem('user-preferences');
    if (savedPreferences) {
      try {
        const prefs = JSON.parse(savedPreferences);
        setSelectedLanguage(prefs.language || 'en');
        setPersonalizationEnabled(prefs.personalization_enabled || false);
        setReadingLevel(prefs.reading_level || 'intermediate');
        setLearningStyle(prefs.learning_style || 'visual');
      } catch (e) {
        console.error('Error parsing saved preferences:', e);
      }
    }
  }, []);

  return (
    <div className="translation-controls" role="region" aria-label="Translation and Personalization Controls">
      <div className="control-header">
        <h3 id="translation-controls-heading">Optional Features</h3>
        <button
          className="toggle-options-btn"
          onClick={() => setShowOptions(!showOptions)}
          aria-expanded={showOptions}
          aria-controls="translation-controls-content"
          aria-describedby="translation-controls-heading"
        >
          {showOptions ? 'Hide Options' : 'Show Options'}
        </button>
      </div>

      {showOptions && (
        <div
          id="translation-controls-content"
          className="controls-container"
          role="group"
          aria-labelledby="translation-controls-heading"
        >
          <div className="control-group">
            <label htmlFor="language-select" id="language-label">
              Translation Language:
            </label>
            <select
              id="language-select"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="language-select"
              aria-labelledby="language-label"
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label htmlFor="personalization-toggle" className="checkbox-label">
              <input
                id="personalization-toggle"
                type="checkbox"
                checked={personalizationEnabled}
                onChange={(e) => setPersonalizationEnabled(e.target.checked)}
                aria-describedby="personalization-desc"
              />
              Enable Content Personalization
            </label>
            <div id="personalization-desc" className="sr-only">
              Enable content personalization based on your learning preferences
            </div>
          </div>

          {personalizationEnabled && (
            <div className="personalization-options" role="group" aria-label="Personalization Options">
              <div className="control-group">
                <label htmlFor="reading-level" id="reading-level-label">
                  Reading Level:
                </label>
                <select
                  id="reading-level"
                  value={readingLevel}
                  onChange={(e) => setReadingLevel(e.target.value)}
                  aria-labelledby="reading-level-label"
                >
                  {readingLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="control-group">
                <label htmlFor="learning-style" id="learning-style-label">
                  Learning Style:
                </label>
                <select
                  id="learning-style"
                  value={learningStyle}
                  onChange={(e) => setLearningStyle(e.target.value)}
                  aria-labelledby="learning-style-label"
                >
                  {learningStyles.map(style => (
                    <option key={style.value} value={style.value}>
                      {style.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          <div className="control-actions" role="group" aria-label="Control Actions">
            <button
              className="apply-btn"
              onClick={applySettings}
              aria-describedby="apply-settings-desc"
            >
              Apply Settings
            </button>
            <button
              className="reset-btn"
              onClick={resetSettings}
              aria-describedby="reset-settings-desc"
            >
              Reset to Default
            </button>
          </div>
          <div id="apply-settings-desc" className="sr-only">
            Apply the selected translation and personalization settings
          </div>
          <div id="reset-settings-desc" className="sr-only">
            Reset all settings to default values
          </div>
        </div>
      )}

      {!showOptions && (
        <div className="quick-actions" role="group" aria-label="Quick Translation Actions">
          <button
            className="translate-btn"
            onClick={() => {
              setSelectedLanguage(selectedLanguage === 'en' ? 'ur' : 'en');
              applySettings();
            }}
            aria-describedby="quick-translate-desc"
          >
            {selectedLanguage === 'en' ? 'Translate to Urdu' : 'Translate to English'}
          </button>
          <div id="quick-translate-desc" className="sr-only">
            Toggle between English and Urdu translation
          </div>
        </div>
      )}

      <style jsx>{`
        .translation-controls {
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 16px;
          margin: 16px 0;
          background-color: #f9f9f9;
        }

        .control-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .control-header h3 {
          margin: 0;
          font-size: 1.1rem;
        }

        .toggle-options-btn {
          background: #007cba;
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
        }

        .controls-container {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .control-group {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .control-group label {
          font-weight: 500;
          font-size: 0.9rem;
        }

        .language-select, select {
          padding: 8px;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .personalization-options {
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          background-color: #fff;
        }

        .control-actions {
          display: flex;
          gap: 12px;
          margin-top: 12px;
        }

        .apply-btn, .reset-btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
        }

        .apply-btn {
          background: #28a745;
          color: white;
        }

        .reset-btn {
          background: #6c757d;
          color: white;
        }

        .quick-actions {
          display: flex;
          gap: 12px;
        }

        .translate-btn {
          background: #007cba;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
        }

        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0, 0, 0, 0);
          white-space: nowrap;
          border: 0;
        }
      `}</style>
    </div>
  );
};

export default TranslationControls;