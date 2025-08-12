exports.up = (pgm) => {
  // Ensure UUID extension exists
  pgm.createExtension("uuid-ossp", { ifNotExists: true });

  // Create users table if it doesn't exist
  pgm.createTable(
    "example",
    {
      id: {
        type: "uuid",
        primaryKey: true,
        default: pgm.func("uuid_generate_v4()"),
      },
      email: { type: "text", unique: true },
      created_at: { type: "timestamptz", default: pgm.func("now()") },
    },
    { ifNotExists: true }
  );
};

exports.down = (pgm) => {
  pgm.dropTable("example", { ifExists: true, cascade: true });
  pgm.dropExtension("uuid-ossp", { ifExists: true });
};
