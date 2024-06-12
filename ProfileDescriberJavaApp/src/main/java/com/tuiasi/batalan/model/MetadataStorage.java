package com.tuiasi.batalan.model;

import com.mongodb.*;
import com.mongodb.client.*;
import com.mongodb.client.result.InsertOneResult;
import org.apache.commons.io.IOUtils;
import org.bson.BsonDocument;
import org.bson.BsonInt64;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.checkerframework.checker.units.qual.A;

import javax.print.Doc;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.*;

import static com.tuiasi.batalan.configs.MongoConstants.*;

public class MetadataStorage {
    private static final String CREDENTIALS_FILE_PATH = "/mongoCreds.txt";
    private final MongoClient mongoClient;
    private final String targetField;

    public MetadataStorage() {
        // Load client secrets.
        String uri;
        try (InputStream in = this.getClass().getResourceAsStream(CREDENTIALS_FILE_PATH)) {
            if (in == null) {
                throw new FileNotFoundException("Resource not found: " + CREDENTIALS_FILE_PATH);
            }
            uri = IOUtils.toString(in, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new RuntimeException("Could not get mongo credentials.", e);
        }

        // Construct a ServerApi instance using the ServerApi.builder() method
        ServerApi serverApi = ServerApi.builder()
                .version(ServerApiVersion.V1)
                .build();
        MongoClientSettings mongoClientSettings = MongoClientSettings.builder()
                .applyConnectionString(new ConnectionString(uri))
                .serverApi(serverApi)
                .build();
        this.mongoClient = MongoClients.create(mongoClientSettings);

        // Connect to the server
        this.targetField = getTargetField();
    }

    public Set<Integer> selectDistinctProfiles() {
        Set<Integer> result = new HashSet<>();
        MongoDatabase db = getAkinatorDB(mongoClient);
        MongoCollection<Document> knowledgeCollection = db.getCollection(KNOWLEDGE_COLLECTION);

        try (MongoCursor<String> cursor = knowledgeCollection.distinct(targetField, String.class).cursor()) {
            while (cursor.hasNext()) {
                String rawId = cursor.next();
                Integer cleanedId = this.cleanRawId(rawId);
                result.add(cleanedId);
            }
        }

        return result;
    }

    public String getTargetField() {
        if (this.targetField != null) {
            return this.targetField;
        }

        MongoDatabase db = getAkinatorDB(mongoClient);
        MongoCollection<Document> metadataCollection = db.getCollection(METADATA_COLLECTION);
        FindIterable<Document> find = metadataCollection.find();

        try (MongoCursor<Document> cursor = find.cursor()) {
            Document metadata = cursor.next();
            return metadata.getString("target_column");
        }
    }

    public void saveToCollection(List<Document> documents, String collectionName) {
        if (!List.of(KNOWLEDGE_COLLECTION, ATTRIBUTE_COLELCTION, METADATA_COLLECTION).contains(collectionName)) {
            System.out.println("Warning: invalid collection name!");
            return;
        }
        MongoDatabase db = getAkinatorDB(mongoClient);
        MongoCollection<Document> collection = db.getCollection(collectionName);
        collection.insertMany(documents);
    }

    public List<String> getQuestions() {
        List<String> result = new ArrayList<>();
        MongoDatabase db = getAkinatorDB(mongoClient);
        MongoCollection<Document> attributesCollection = db.getCollection(ATTRIBUTE_COLELCTION);
        for (Document doc : attributesCollection.find()) {
            result.add(doc.getString("_id"));
        }

        return result;
    }

    public boolean insertQuestion(String questionName) {
        MongoDatabase db = getAkinatorDB(mongoClient);
        MongoCollection<Document> attributeCollection = db.getCollection(ATTRIBUTE_COLELCTION);
        try {
            InsertOneResult result = attributeCollection.insertOne(new Document()
                    .append("_id", questionName)
                    .append("values", Arrays.asList("Yes", "No")));
            return result.wasAcknowledged();
        } catch (MongoWriteException e) {
            return false;
        }
    }

    private MongoDatabase getAkinatorDB(MongoClient mongoClient) {
        return mongoClient.getDatabase(DATABASE_NAME);
    }

    private Integer cleanRawId(String rawId) {
        return Integer.parseInt(rawId.split("\\.")[0]);
    }
}
