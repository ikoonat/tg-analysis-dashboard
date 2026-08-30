import React from 'react';

const FileUploader = ({ onFileLoad, loading }) => {
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                onFileLoad(e.target.result);
            };
            reader.readAsText(file);
        }
    };

    return (
        <div className="inline-block">
            <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="csv-upload"
                disabled={loading}
            />
            <label
                htmlFor="csv-upload"
                className={`px-4 py-2 bg-blue-500 text-white rounded cursor-pointer hover:bg-blue-600 transition ${loading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
            >
                {loading ? 'Loading...' : 'Upload CSV'}
            </label>
        </div>
    );
};

export default FileUploader;