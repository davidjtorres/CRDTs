import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axiosInstance from './../AxiosInstance';
import * as Y from 'yjs';
import { QuillBinding } from 'y-quill';
import Editor from './../Editor/Editor';

const ORIGIN_REMOTE = 'remote';

const DocumentEditor = () => {
    const { document_id } = useParams();
    const [document, setDocument] = useState(null);
    const wsRef = useRef(null);
    const documentRef = useRef(new Y.Doc());
    const quillRef = useRef();

    const connect_socket = () => {
        if (wsRef.current) return;
        const ws = new WebSocket(
            `http://localhost:8000/ws/documents/${document_id}/?token=${localStorage.getItem("token")}`
        );
        ws.binaryType = 'arraybuffer';
        wsRef.current = ws;
        ws.onopen = () => {
            console.log('socket connected');
        };
        ws.onclose = () => {
            console.log('socket disconnected');
        }

        ws.onmessage = (event) => {
            documentRef.current.transact(() => {
                const update = new Uint8Array(event.data);
                Y.applyUpdate(documentRef.current, update);
            }, ORIGIN_REMOTE);
        };
    };

    const bind_document = () => {
        // Bind Yjs document to Quill editor

        const handleUpdate = (update, origin) => {
            // Only send updates that originated locally
            if (origin != ORIGIN_REMOTE) {
                wsRef.current.send(update);
            }
        };

        documentRef.current.on('update', handleUpdate);

        let quill = quillRef.current;

        //Binding Quill to Yjs document
        const binding = new QuillBinding(
            documentRef.current.getText('content'),
            quill
        );
    };

    useEffect(() => {
        const fetchDocument = async () => {
            try {
                const response = await axiosInstance.get(
                    `/documents/${document_id}`
                );
                setDocument(response.data);
                connect_socket();
            } catch (error) {
                console.error('Failed to fetch document', error);
            }
        };

        fetchDocument();
    }, [document_id]);

    if (!document) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>{document.title}</h2>
            <div className="App">
                <Editor
                    ref={quillRef}
                    readOnly={false}
                    onReady={() => {
                        bind_document();
                    }}
                />
            </div>
        </div>
    );
};

export default DocumentEditor;
