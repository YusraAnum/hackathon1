import React from 'react';
import { useLocation } from '@docusaurus/router';
import queryString from 'query-string';
import TextbookViewer from '../components/TextbookViewer';

const ChapterPage = () => {
  const location = useLocation();
  const queryParams = queryString.parse(location.search);
  const chapterId = location.pathname.split('/').pop() || queryParams.chapterId || location.state?.chapterId;

  return (
    <div className="chapter-page">
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <TextbookViewer chapterId={chapterId} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChapterPage;